from datetime import datetime
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


def test_user_creation(session, sample_user):
    session.add(sample_user)
    session.commit()

    user = session.get(User, sample_user.id)
    assert user.username == "testuser"
    assert user.level == 5
    assert user.wanikani_api_key == "test-wanikani-key"
    assert user.mcp_api_key == "test-mcp-key"


def test_subject_creation(session, sample_subject):
    session.add(sample_subject)
    session.commit()

    subject = session.get(Subject, 1)
    assert subject.object_type == SubjectType.KANJI
    assert subject.characters == "一"
    assert subject.level == 1
    assert subject.meanings == [{"meaning": "one", "primary": True}]
    assert subject.readings == [{"reading": "いち", "primary": True, "type": "onyomi"}]


def test_assignment_relationship(session, sample_user, sample_subject):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    assignment = Assignment(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
        subject_type=SubjectType.KANJI,
        srs_stage=1,
        available_at=datetime.utcnow(),
    )
    session.add(assignment)
    session.commit()

    # Test relationships
    user = session.get(User, sample_user.id)
    assert len(user.assignments) == 1
    assert user.assignments[0].subject.characters == "一"
    assert user.assignments[0].subject_type == SubjectType.KANJI


def test_review_statistic_creation(session, sample_user, sample_subject):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    stat = ReviewStatistic(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
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
    session.add(stat)
    session.commit()

    saved_stat = session.get(ReviewStatistic, 1)
    assert saved_stat.percentage_correct == 75
    assert saved_stat.meaning_incorrect == 2
    assert saved_stat.subject_type == SubjectType.KANJI


# Test all subject types
def test_subject_types(session, sample_radical, sample_vocabulary):
    session.add(sample_radical)
    session.add(sample_vocabulary)
    session.commit()

    radical = session.get(Subject, 2)
    vocab = session.get(Subject, 3)

    assert radical.object_type == SubjectType.RADICAL
    assert radical.readings is None  # Radicals don't have readings

    assert vocab.object_type == SubjectType.VOCABULARY
    assert vocab.component_subject_ids == [1]


def test_srs_stage_creation(session, sample_srs_stage):
    session.add(sample_srs_stage)
    session.commit()

    stage = session.get(SrsStage, 1)
    assert stage.position == 1
    assert stage.interval == 14400000
    assert stage.interval_unit == "milliseconds"


def test_level_progression(session, sample_user, sample_level_progression):
    session.add(sample_user)
    session.commit()

    sample_level_progression.user_id = sample_user.id
    session.add(sample_level_progression)
    session.commit()

    progression = session.get(LevelProgression, 1)
    assert progression.level == 2
    assert progression.user.username == "testuser"


def test_study_material_creation(
    session, sample_user, sample_subject, sample_study_material
):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    sample_study_material.user_id = sample_user.id
    sample_study_material.subject_id = sample_subject.id
    session.add(sample_study_material)
    session.commit()

    material = session.get(StudyMaterial, 1)
    assert material.meaning_note == "Remember: horizontal line like the ground"
    assert material.meaning_synonyms == ["1", "single", "unity"]
    assert material.subject_type == SubjectType.KANJI


def test_voice_actor_creation(session, sample_voice_actor):
    session.add(sample_voice_actor)
    session.commit()

    actor = session.get(VoiceActor, 1)
    assert actor.name == "Kyoko"
    assert actor.gender == "female"


def test_sync_log_creation(session, sample_user, sample_sync_log):
    session.add(sample_user)
    session.commit()

    sample_sync_log.user_id = sample_user.id
    session.add(sample_sync_log)
    session.commit()

    log = session.get(SyncLog, 1)
    assert log.sync_type == SyncType.INCREMENTAL
    assert log.status == SyncStatus.SUCCESS
    assert log.records_updated == 15


def test_review_creation(session, sample_user, sample_subject, sample_review):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    sample_review.user_id = sample_user.id
    sample_review.subject_id = sample_subject.id
    session.add(sample_review)
    session.commit()

    review = session.get(Review, 1)
    assert review.starting_srs_stage == 2
    assert review.ending_srs_stage == 3
    assert review.incorrect_meaning_answers == 1
    assert review.incorrect_reading_answers == 0


def test_user_relationships(session, sample_user, sample_subject):
    """Test that all user relationships work correctly"""
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    # Create assignment
    assignment = Assignment(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
        subject_type=SubjectType.KANJI,
        srs_stage=1,
    )
    session.add(assignment)

    # Create review
    review = Review(
        id=1,
        user_id=sample_user.id,
        assignment_id=assignment.id,
        subject_id=sample_subject.id,
        starting_srs_stage=1,
        ending_srs_stage=2,
    )
    session.add(review)

    # Create review statistic
    stat = ReviewStatistic(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
        subject_type=SubjectType.KANJI,
        percentage_correct=80,
    )
    session.add(stat)

    session.commit()

    # Test all relationships work
    user = session.get(User, sample_user.id)
    assert len(user.assignments) == 1
    assert len(user.reviews) == 1
    assert len(user.review_stats) == 1

    subject = session.get(Subject, sample_subject.id)
    assert len(subject.assignments) == 1
    assert len(subject.reviews) == 1
    assert len(subject.review_stats) == 1


def test_enum_values():
    """Test that our enums work correctly"""
    assert SubjectType.KANJI == "kanji"
    assert SubjectType.RADICAL == "radical"
    assert SubjectType.VOCABULARY == "vocabulary"

    assert SyncStatus.SUCCESS == "success"
    assert SyncStatus.ERROR == "error"
    assert SyncStatus.IN_PROGRESS == "in_progress"

    assert SyncType.FULL == "full"
    assert SyncType.INCREMENTAL == "incremental"
    assert SyncType.MANUAL == "manual"
