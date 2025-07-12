from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class SubjectType(str, Enum):
    RADICAL = "radical"
    KANJI = "kanji"
    VOCABULARY = "vocabulary"
    KANA_VOCABULARY = "kana_vocabulary"


class SyncStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"


class SyncType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    MANUAL = "manual"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    wanikani_api_key: str = Field(unique=True, index=True)
    mcp_api_key: str = Field(unique=True, index=True)
    username: str = Field(index=True)
    level: int = Field(index=True)
    profile_url: str | None = None
    started_at: datetime | None = None
    subscription_active: bool = Field(default=False)
    subscription_type: str | None = None
    subscription_max_level_granted: int | None = None
    subscription_period_ends_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_sync: datetime | None = None

    assignments: list["Assignment"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    review_stats: list["ReviewStatistic"] = Relationship(back_populates="user")
    level_progressions: list["LevelProgression"] = Relationship(back_populates="user")
    study_materials: list["StudyMaterial"] = Relationship(back_populates="user")
    sync_logs: list["SyncLog"] = Relationship(back_populates="user")


class Subject(SQLModel, table=True):
    id: int = Field(primary_key=True)
    object_type: SubjectType = Field(index=True)
    level: int = Field(index=True)
    slug: str = Field(index=True)
    characters: str | None = None
    meanings: list[dict[str, Any]] = Field(sa_column=Column(JSON))
    readings: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    component_subject_ids: list[int] | None = Field(
        default=None, sa_column=Column(JSON)
    )
    amalgamation_subject_ids: list[int] | None = Field(
        default=None, sa_column=Column(JSON)
    )
    document_url: str
    hidden_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    assignments: list["Assignment"] = Relationship(back_populates="subject")
    reviews: list["Review"] = Relationship(back_populates="subject")
    review_stats: list["ReviewStatistic"] = Relationship(back_populates="subject")
    study_materials: list["StudyMaterial"] = Relationship(back_populates="subject")


class Assignment(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    subject_type: SubjectType
    srs_stage: int = Field(index=True)
    unlocked_at: datetime | None = None
    started_at: datetime | None = None
    passed_at: datetime | None = None
    burned_at: datetime | None = None
    available_at: datetime | None = Field(default=None, index=True)
    resurrected_at: datetime | None = None
    hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    user: User = Relationship(back_populates="assignments")
    subject: Subject = Relationship(back_populates="assignments")


class Review(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    assignment_id: int = Field(index=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    starting_srs_stage: int
    ending_srs_stage: int
    incorrect_meaning_answers: int = Field(default=0)
    incorrect_reading_answers: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    user: User = Relationship(back_populates="reviews")
    subject: Subject = Relationship(back_populates="reviews")


class ReviewStatistic(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    subject_type: SubjectType
    meaning_correct: int = Field(default=0)
    meaning_incorrect: int = Field(default=0)
    meaning_max_streak: int = Field(default=0)
    meaning_current_streak: int = Field(default=0)
    reading_correct: int = Field(default=0)
    reading_incorrect: int = Field(default=0)
    reading_max_streak: int = Field(default=0)
    reading_current_streak: int = Field(default=0)
    percentage_correct: int = Field(default=0)
    hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    user: User = Relationship(back_populates="review_stats")
    subject: Subject = Relationship(back_populates="review_stats")


class SrsStage(SQLModel, table=True):
    id: int = Field(primary_key=True)
    position: int = Field(unique=True, index=True)
    meaning_correct: int
    meaning_incorrect: int
    reading_correct: int
    reading_incorrect: int
    interval: int
    interval_unit: str  # milliseconds, seconds, minutes, hours, days, weeks


class LevelProgression(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    level: int = Field(index=True)
    unlocked_at: datetime | None = None
    started_at: datetime | None = None
    passed_at: datetime | None = None
    completed_at: datetime | None = None
    abandoned_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    user: User = Relationship(back_populates="level_progressions")


class StudyMaterial(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    subject_type: SubjectType
    meaning_note: str | None = None
    reading_note: str | None = None
    meaning_synonyms: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_updated_at: datetime | None = None

    user: User = Relationship(back_populates="study_materials")
    subject: Subject = Relationship(back_populates="study_materials")


class VoiceActor(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str
    gender: str


class SyncLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    sync_type: SyncType
    status: SyncStatus
    records_updated: int = 0
    error_message: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    user: User = Relationship(back_populates="sync_logs")
