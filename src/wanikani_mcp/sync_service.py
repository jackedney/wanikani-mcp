from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import logging

from .database import get_engine
from .models import (
    User,
    Subject,
    Assignment,
    ReviewStatistic,
    SyncLog,
    SyncType,
    SyncStatus,
)
from .wanikani_client import WaniKaniClient
from .config import settings

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def start(self):
        """Start the background sync scheduler"""
        if self.is_running:
            return

        # Schedule user syncs based on configuration
        self.scheduler.add_job(
            self._sync_all_users,
            trigger=IntervalTrigger(minutes=settings.sync_interval_minutes),
            id="sync_all_users",
            name="Sync all users",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,  # 5 minutes
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Background sync service started")

    async def stop(self):
        """Stop the background sync scheduler"""
        if not self.is_running:
            return

        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("Background sync service stopped")

    async def _sync_all_users(self):
        """Sync data for all active users"""
        engine = get_engine()

        with Session(engine) as session:
            # Get users who haven't synced in the last hour
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            # Get users who need syncing (no last_sync or stale sync)
            no_sync_users = session.exec(
                select(User).where(User.last_sync is None)
            ).all()
            stale_sync_users = session.exec(
                select(User).where(User.last_sync < cutoff_time)
            ).all()
            users_to_sync = list(set(no_sync_users + stale_sync_users))

        if not users_to_sync:
            logger.info("No users need syncing")
            return

        logger.info(f"Starting background sync for {len(users_to_sync)} users")

        # Sync users concurrently (but limit concurrency)
        semaphore = asyncio.Semaphore(settings.max_concurrent_syncs)

        async def sync_user_with_semaphore(user: User):
            async with semaphore:
                try:
                    await self._sync_user_data(user)
                    logger.info(f"Successfully synced user {user.username}")
                except Exception as e:
                    logger.error(f"Failed to sync user {user.username}: {e}")

        tasks = [sync_user_with_semaphore(user) for user in users_to_sync]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Background sync completed")

    async def _sync_user_data(self, user: User) -> int:
        """Sync data for a single user"""
        engine = get_engine()

        # Create sync log
        with Session(engine) as session:
            sync_log = SyncLog(
                user_id=user.id,
                sync_type=SyncType.INCREMENTAL,
                status=SyncStatus.IN_PROGRESS,
                started_at=datetime.now(timezone.utc),
            )
            session.add(sync_log)
            session.commit()
            session.refresh(sync_log)

        try:
            client = WaniKaniClient(user.wanikani_api_key)
            records_updated = 0

            # Get last sync time for incremental updates
            # For new users (no last_sync), do a full sync
            last_sync = user.last_sync

            # Update user profile
            user_data = await client.get_user()
            with Session(engine) as session:
                db_user = session.get(User, user.id)
                if db_user:
                    db_user.username = user_data["data"]["username"]
                    db_user.level = user_data["data"]["level"]
                    db_user.profile_url = user_data["data"]["profile_url"]

                    # Update subscription info if available
                    subscription = user_data["data"].get("subscription")
                    if subscription:
                        db_user.subscription_active = subscription["active"]
                        db_user.subscription_type = subscription["type"]
                        db_user.subscription_max_level_granted = subscription[
                            "max_level_granted"
                        ]
                        if subscription.get("period_ends_at"):
                            db_user.subscription_period_ends_at = (
                                datetime.fromisoformat(
                                    subscription["period_ends_at"].replace(
                                        "Z", "+00:00"
                                    )
                                )
                            )

                    db_user.last_sync = datetime.now(timezone.utc)
                    session.add(db_user)
                    session.commit()
                    records_updated += 1

            # Skip subjects sync for now - too much data, focus on assignments
            # subjects_data = await client.get_subjects(updated_after=last_sync)
            # for subject_data in subjects_data:
            #     if "data" in subject_data:
            #         await self._upsert_subject(subject_data["data"])
            #         records_updated += 1
            #     else:
            #         await self._upsert_subject(subject_data)
            #         records_updated += 1

            # Sync assignments
            try:
                assignments_data = await client.get_assignments(updated_after=last_sync)
                logger.info(
                    f"Syncing {len(assignments_data)} assignments for user {user.username}"
                )

                for i, assignment_item in enumerate(assignments_data):
                    try:
                        # Handle the nested structure: top-level has id, data has the actual assignment info
                        assignment_id = assignment_item.get("id")
                        assignment_data = assignment_item.get("data", assignment_item)

                        # Add the ID to the data for processing
                        if assignment_id:
                            assignment_data["id"] = assignment_id
                            await self._upsert_assignment(user.id, assignment_data)
                            records_updated += 1

                            # Log progress for large syncs
                            if (i + 1) % 500 == 0:
                                logger.info(
                                    f"Synced {i + 1}/{len(assignments_data)} assignments"
                                )
                    except Exception as e:
                        logger.error(f"Error syncing assignment {assignment_id}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error getting assignments: {e}")
                # Continue with review stats sync even if assignments fail

            # Sync review statistics
            try:
                review_stats_data = await client.get_review_statistics(
                    updated_after=last_sync
                )
                logger.info(
                    f"Syncing {len(review_stats_data)} review statistics for user {user.username}"
                )

                for i, stats_item in enumerate(review_stats_data):
                    try:
                        # Handle the nested structure: top-level has id, data has the actual stats info
                        stats_id = stats_item.get("id")
                        stats_data = stats_item.get("data", stats_item)

                        # Add the ID to the data for processing
                        if stats_id:
                            stats_data["id"] = stats_id
                            await self._upsert_review_statistic(user.id, stats_data)
                            records_updated += 1

                            # Log progress for large syncs
                            if (i + 1) % 500 == 0:
                                logger.info(
                                    f"Synced {i + 1}/{len(review_stats_data)} review statistics"
                                )
                    except Exception as e:
                        logger.error(f"Error syncing review stat {stats_id}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error getting review statistics: {e}")

            await client.close()

            # Update sync log
            with Session(engine) as session:
                db_sync_log = session.get(SyncLog, sync_log.id)
                if db_sync_log:
                    db_sync_log.status = SyncStatus.SUCCESS
                    db_sync_log.records_updated = records_updated
                    db_sync_log.completed_at = datetime.now(timezone.utc)
                    session.add(db_sync_log)
                    session.commit()

            return records_updated

        except Exception as e:
            # Update sync log with error
            with Session(engine) as session:
                db_sync_log = session.get(SyncLog, sync_log.id)
                if db_sync_log:
                    db_sync_log.status = SyncStatus.ERROR
                    db_sync_log.error_message = str(e)
                    db_sync_log.completed_at = datetime.now(timezone.utc)
                    session.add(db_sync_log)
                    session.commit()
            raise

    async def _upsert_subject(self, subject_data: dict):
        """Insert or update a subject record"""
        engine = get_engine()

        with Session(engine) as session:
            existing_subject = session.get(Subject, subject_data["id"])

            if existing_subject:
                # Update existing
                existing_subject.level = subject_data["level"]
                existing_subject.slug = subject_data["slug"]
                existing_subject.characters = subject_data.get("characters")
                existing_subject.meanings = subject_data["meanings"]
                existing_subject.readings = subject_data.get("readings")
                existing_subject.component_subject_ids = subject_data.get(
                    "component_subject_ids"
                )
                existing_subject.amalgamation_subject_ids = subject_data.get(
                    "amalgamation_subject_ids"
                )
                existing_subject.document_url = subject_data["document_url"]
                existing_subject.data_updated_at = datetime.fromisoformat(
                    subject_data["data_updated_at"].replace("Z", "+00:00")
                )
                if subject_data.get("hidden_at"):
                    existing_subject.hidden_at = datetime.fromisoformat(
                        subject_data["hidden_at"].replace("Z", "+00:00")
                    )
                session.add(existing_subject)
            else:
                # Create new
                subject = Subject(
                    id=subject_data["id"],
                    object_type=subject_data["object"],
                    level=subject_data["level"],
                    slug=subject_data["slug"],
                    characters=subject_data.get("characters"),
                    meanings=subject_data["meanings"],
                    readings=subject_data.get("readings"),
                    component_subject_ids=subject_data.get("component_subject_ids"),
                    amalgamation_subject_ids=subject_data.get(
                        "amalgamation_subject_ids"
                    ),
                    document_url=subject_data["document_url"],
                    data_updated_at=datetime.fromisoformat(
                        subject_data["data_updated_at"].replace("Z", "+00:00")
                    ),
                    hidden_at=datetime.fromisoformat(
                        subject_data["hidden_at"].replace("Z", "+00:00")
                    )
                    if subject_data.get("hidden_at")
                    else None,
                )
                session.add(subject)

            session.commit()

    async def _upsert_assignment(self, user_id: int, assignment_data: dict):
        """Insert or update an assignment record"""
        engine = get_engine()

        # Get the assignment ID from the right place
        assignment_id = assignment_data.get("id")
        if not assignment_id:
            # Skip assignments without IDs
            return

        with Session(engine) as session:
            existing_assignment = session.get(Assignment, assignment_id)

            if existing_assignment:
                # Update existing
                existing_assignment.srs_stage = assignment_data["srs_stage"]
                existing_assignment.unlocked_at = (
                    datetime.fromisoformat(
                        assignment_data["unlocked_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("unlocked_at")
                    else None
                )
                existing_assignment.started_at = (
                    datetime.fromisoformat(
                        assignment_data["started_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("started_at")
                    else None
                )
                existing_assignment.passed_at = (
                    datetime.fromisoformat(
                        assignment_data["passed_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("passed_at")
                    else None
                )
                existing_assignment.burned_at = (
                    datetime.fromisoformat(
                        assignment_data["burned_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("burned_at")
                    else None
                )
                existing_assignment.available_at = (
                    datetime.fromisoformat(
                        assignment_data["available_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("available_at")
                    else None
                )
                existing_assignment.resurrected_at = (
                    datetime.fromisoformat(
                        assignment_data["resurrected_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("resurrected_at")
                    else None
                )
                existing_assignment.hidden = assignment_data.get("hidden", False)
                existing_assignment.data_updated_at = datetime.now(timezone.utc)
                session.add(existing_assignment)
            else:
                # Create new
                assignment = Assignment(
                    id=assignment_id,
                    user_id=user_id,
                    subject_id=assignment_data["subject_id"],
                    subject_type=assignment_data["subject_type"],
                    srs_stage=assignment_data["srs_stage"],
                    unlocked_at=datetime.fromisoformat(
                        assignment_data["unlocked_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("unlocked_at")
                    else None,
                    started_at=datetime.fromisoformat(
                        assignment_data["started_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("started_at")
                    else None,
                    passed_at=datetime.fromisoformat(
                        assignment_data["passed_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("passed_at")
                    else None,
                    burned_at=datetime.fromisoformat(
                        assignment_data["burned_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("burned_at")
                    else None,
                    available_at=datetime.fromisoformat(
                        assignment_data["available_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("available_at")
                    else None,
                    resurrected_at=datetime.fromisoformat(
                        assignment_data["resurrected_at"].replace("Z", "+00:00")
                    )
                    if assignment_data.get("resurrected_at")
                    else None,
                    hidden=assignment_data.get("hidden", False),
                    data_updated_at=datetime.now(timezone.utc),
                )
                session.add(assignment)

            session.commit()

    async def _upsert_review_statistic(self, user_id: int, stats_data: dict):
        """Insert or update a review statistic record"""
        engine = get_engine()

        with Session(engine) as session:
            existing_stats = session.get(ReviewStatistic, stats_data["id"])

            if existing_stats:
                # Update existing
                existing_stats.meaning_correct = stats_data["meaning_correct"]
                existing_stats.meaning_incorrect = stats_data["meaning_incorrect"]
                existing_stats.meaning_max_streak = stats_data["meaning_max_streak"]
                existing_stats.meaning_current_streak = stats_data[
                    "meaning_current_streak"
                ]
                existing_stats.reading_correct = stats_data["reading_correct"]
                existing_stats.reading_incorrect = stats_data["reading_incorrect"]
                existing_stats.reading_max_streak = stats_data["reading_max_streak"]
                existing_stats.reading_current_streak = stats_data[
                    "reading_current_streak"
                ]
                existing_stats.percentage_correct = stats_data["percentage_correct"]
                existing_stats.hidden = stats_data["hidden"]
                existing_stats.data_updated_at = datetime.fromisoformat(
                    stats_data["data_updated_at"].replace("Z", "+00:00")
                )
                session.add(existing_stats)
            else:
                # Create new
                review_stat = ReviewStatistic(
                    id=stats_data["id"],
                    user_id=user_id,
                    subject_id=stats_data["subject_id"],
                    subject_type=stats_data["subject_type"],
                    meaning_correct=stats_data["meaning_correct"],
                    meaning_incorrect=stats_data["meaning_incorrect"],
                    meaning_max_streak=stats_data["meaning_max_streak"],
                    meaning_current_streak=stats_data["meaning_current_streak"],
                    reading_correct=stats_data["reading_correct"],
                    reading_incorrect=stats_data["reading_incorrect"],
                    reading_max_streak=stats_data["reading_max_streak"],
                    reading_current_streak=stats_data["reading_current_streak"],
                    percentage_correct=stats_data["percentage_correct"],
                    hidden=stats_data["hidden"],
                    data_updated_at=datetime.fromisoformat(
                        stats_data["data_updated_at"].replace("Z", "+00:00")
                    ),
                )
                session.add(review_stat)

            session.commit()


# Global sync service instance
sync_service = SyncService()
