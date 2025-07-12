import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, create_engine, Session
from wanikani_mcp.models import (
    User,
    Subject,
    Assignment,
    Review,
    ReviewStatistic,
    SrsStage,
    LevelProgression,
    StudyMaterial,
    VoiceActor,
    SyncLog,
    SubjectType,
    SyncStatus,
    SyncType,
)


@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def session(engine):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_user():
    return User(
        wanikani_api_key="test-wanikani-key",
        mcp_api_key="test-mcp-key",
        username="testuser",
        level=5,
    )


@pytest.fixture
def sample_subject():
    return Subject(
        id=1,
        object_type=SubjectType.KANJI,
        level=1,
        slug="一",
        characters="一",
        meanings=[{"meaning": "one", "primary": True}],
        readings=[{"reading": "いち", "primary": True, "type": "onyomi"}],
        document_url="https://www.wanikani.com/kanji/一",
    )


@pytest.fixture
def sample_radical():
    return Subject(
        id=2,
        object_type=SubjectType.RADICAL,
        level=1,
        slug="ground",
        characters="一",
        meanings=[{"meaning": "ground", "primary": True}],
        document_url="https://www.wanikani.com/radicals/ground",
    )


@pytest.fixture
def sample_vocabulary():
    return Subject(
        id=3,
        object_type=SubjectType.VOCABULARY,
        level=1,
        slug="一つ",
        characters="一つ",
        meanings=[{"meaning": "one thing", "primary": True}],
        readings=[{"reading": "ひとつ", "primary": True}],
        component_subject_ids=[1],
        document_url="https://www.wanikani.com/vocabulary/一つ",
    )


@pytest.fixture
def sample_assignment(sample_user, sample_subject):
    return Assignment(
        id=1,
        user_id=1,  # Will be set properly in tests
        subject_id=1,  # Will be set properly in tests
        subject_type=SubjectType.KANJI,
        srs_stage=3,
        unlocked_at=datetime.now(timezone.utc) - timedelta(days=7),
        started_at=datetime.now(timezone.utc) - timedelta(days=6),
        available_at=datetime.now(timezone.utc) + timedelta(hours=4),
    )


@pytest.fixture
def sample_review(sample_user, sample_subject):
    return Review(
        id=1,
        user_id=1,
        assignment_id=1,
        subject_id=1,
        starting_srs_stage=2,
        ending_srs_stage=3,
        incorrect_meaning_answers=1,
        incorrect_reading_answers=0,
    )


@pytest.fixture
def sample_review_statistic(sample_user, sample_subject):
    return ReviewStatistic(
        id=1,
        user_id=1,
        subject_id=1,
        subject_type=SubjectType.KANJI,
        meaning_correct=8,
        meaning_incorrect=2,
        meaning_max_streak=5,
        meaning_current_streak=3,
        reading_correct=7,
        reading_incorrect=3,
        reading_max_streak=4,
        reading_current_streak=2,
        percentage_correct=75,
    )


@pytest.fixture
def sample_srs_stage():
    return SrsStage(
        id=1,
        position=1,
        meaning_correct=1,
        meaning_incorrect=0,
        reading_correct=1,
        reading_incorrect=0,
        interval=14400000,  # 4 hours in milliseconds
        interval_unit="milliseconds",
    )


@pytest.fixture
def sample_level_progression(sample_user):
    return LevelProgression(
        id=1,
        user_id=1,
        level=2,
        unlocked_at=datetime.now(timezone.utc) - timedelta(days=30),
        started_at=datetime.now(timezone.utc) - timedelta(days=25),
        passed_at=datetime.now(timezone.utc) - timedelta(days=5),
        completed_at=datetime.now(timezone.utc) - timedelta(days=1),
    )


@pytest.fixture
def sample_study_material(sample_user, sample_subject):
    return StudyMaterial(
        id=1,
        user_id=1,
        subject_id=1,
        subject_type=SubjectType.KANJI,
        meaning_note="Remember: horizontal line like the ground",
        meaning_synonyms=["1", "single", "unity"],
    )


@pytest.fixture
def sample_voice_actor():
    return VoiceActor(
        id=1,
        name="Kyoko",
        description="Standard female voice",
        gender="female",
    )


@pytest.fixture
def sample_sync_log(sample_user):
    return SyncLog(
        id=1,
        user_id=1,
        sync_type=SyncType.INCREMENTAL,
        status=SyncStatus.SUCCESS,
        records_updated=15,
        completed_at=datetime.now(timezone.utc),
    )
