from wanikani_mcp.database import get_session
from sqlmodel import SQLModel, create_engine


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
        "synclog",
    ]

    for table in expected_tables:
        assert table in table_names
