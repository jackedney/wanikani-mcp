from datetime import datetime
from wanikani_mcp.models import User, Subject, Assignment, ReviewStatistic


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
    assert subject.object_type == "kanji"
    assert subject.characters == "一"
    assert subject.level == 1


def test_assignment_relationship(session, sample_user, sample_subject):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    assignment = Assignment(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
        subject_type="kanji",
        srs_stage=1,
        available_at=datetime.utcnow(),
    )
    session.add(assignment)
    session.commit()

    # Test relationships
    user = session.get(User, sample_user.id)
    assert len(user.assignments) == 1
    assert user.assignments[0].subject.characters == "一"


def test_review_statistic_creation(session, sample_user, sample_subject):
    session.add(sample_user)
    session.add(sample_subject)
    session.commit()

    stat = ReviewStatistic(
        id=1,
        user_id=sample_user.id,
        subject_id=sample_subject.id,
        subject_type="kanji",
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
