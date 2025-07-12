import secrets
import hashlib
from sqlmodel import Session, select
from .models import User


def generate_mcp_api_key() -> str:
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


async def create_user_with_api_keys(
    wanikani_api_key: str, username: str, level: int, session: Session
) -> tuple[User, str]:
    mcp_api_key = generate_mcp_api_key()

    user = User(
        wanikani_api_key=wanikani_api_key,
        mcp_api_key=mcp_api_key,
        username=username,
        level=level,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user, mcp_api_key


async def verify_mcp_api_key(api_key: str, session: Session) -> User | None:
    user = session.exec(select(User).where(User.mcp_api_key == api_key)).first()
    return user
