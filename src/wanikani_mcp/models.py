from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum


class SubjectType(str, Enum):
    RADICAL = "radical"
    KANJI = "kanji"
    VOCABULARY = "vocabulary"


class SyncStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"


class SyncType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    MANUAL = "manual"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wanikani_api_key: str = Field(unique=True, index=True)
    mcp_api_key: str = Field(unique=True, index=True)
    username: str = Field(index=True)
    level: int = Field(index=True)
    profile_url: Optional[str] = None
    started_at: Optional[datetime] = None
    subscription_active: bool = Field(default=False)
    subscription_type: Optional[str] = None
    subscription_max_level_granted: Optional[int] = None
    subscription_period_ends_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None

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
    characters: Optional[str] = None
    meanings: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    readings: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    component_subject_ids: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))
    amalgamation_subject_ids: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))
    document_url: str
    hidden_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

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
    unlocked_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    passed_at: Optional[datetime] = None
    burned_at: Optional[datetime] = None
    available_at: Optional[datetime] = Field(default=None, index=True)
    resurrected_at: Optional[datetime] = None
    hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

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
    unlocked_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    passed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    abandoned_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

    user: User = Relationship(back_populates="level_progressions")


class StudyMaterial(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    subject_type: SubjectType
    meaning_note: Optional[str] = None
    reading_note: Optional[str] = None
    meaning_synonyms: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    hidden: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_updated_at: Optional[datetime] = None

    user: User = Relationship(back_populates="study_materials")
    subject: Subject = Relationship(back_populates="study_materials")


class VoiceActor(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str
    gender: str


class SyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    sync_type: SyncType
    status: SyncStatus
    records_updated: int = 0
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    user: User = Relationship(back_populates="sync_logs")
