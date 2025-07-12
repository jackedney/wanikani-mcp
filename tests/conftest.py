import pytest
from sqlmodel import SQLModel, create_engine, Session
from wanikani_mcp.models import User, Subject


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
        object_type="kanji",
        level=1,
        slug="一",
        characters="一",
        meanings='[{"meaning": "one", "primary": true}]',
        readings='[{"reading": "いち", "primary": true}]',
        document_url="https://www.wanikani.com/kanji/一",
    )
