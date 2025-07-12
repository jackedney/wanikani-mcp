from sqlmodel import Session, SQLModel, create_engine

from wanikani_mcp.database import get_session


def test_get_session():
    sessions = list(get_session())
    assert len(sessions) == 1


def test_create_tables():
    engine = create_engine("sqlite:///:memory:")

    # Should not raise any exceptions
    SQLModel.metadata.create_all(engine)

    # Verify tables exist by checking metadata
    table_names = [table.name for table in SQLModel.metadata.tables.values()]
    expected_tables = [
        "user",
        "subject",
        "assignment",
        "review",
        "reviewstatistic",
        "srsstage",
        "levelprogression",
        "studymaterial",
        "voiceactor",
        "synclog",
    ]

    for table in expected_tables:
        assert table in table_names


def test_database_indexes():
    """Test that important indexes are created"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    # Check that key indexes exist
    from sqlalchemy import inspect

    inspector = inspect(engine)

    # Check user table indexes
    user_indexes = inspector.get_indexes("user")
    index_names = [idx["name"] for idx in user_indexes]
    assert "ix_user_wanikani_api_key" in index_names
    assert "ix_user_mcp_api_key" in index_names
    assert "ix_user_username" in index_names

    # Check subject table indexes
    subject_indexes = inspector.get_indexes("subject")
    subject_index_names = [idx["name"] for idx in subject_indexes]
    assert "ix_subject_level" in subject_index_names
    assert "ix_subject_object_type" in subject_index_names


def test_database_foreign_keys():
    """Test that foreign key relationships work"""
    from wanikani_mcp.models import Assignment, Subject, User

    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create user and subject
        user = User(
            wanikani_api_key="test-key",
            mcp_api_key="test-mcp",
            username="test",
            level=1,
        )
        subject = Subject(
            id=1,
            object_type="kanji",
            level=1,
            slug="test",
            meanings=[],
            document_url="http://test.com",
        )
        session.add(user)
        session.add(subject)
        session.commit()

        # Create assignment with foreign keys
        assignment = Assignment(
            id=1,
            user_id=user.id,
            subject_id=subject.id,
            subject_type="kanji",
            srs_stage=1,
        )
        session.add(assignment)
        session.commit()

        # Test the relationship works
        retrieved_assignment = session.get(Assignment, 1)
        assert retrieved_assignment is not None
        assert retrieved_assignment.user.username == "test"
        assert retrieved_assignment.subject.slug == "test"
