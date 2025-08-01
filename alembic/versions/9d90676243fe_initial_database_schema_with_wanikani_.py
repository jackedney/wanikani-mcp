"""Initial database schema with WaniKani models

Revision ID: 9d90676243fe
Revises:
Create Date: 2025-07-12 13:15:05.556870

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d90676243fe"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "srsstage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("meaning_correct", sa.Integer(), nullable=False),
        sa.Column("meaning_incorrect", sa.Integer(), nullable=False),
        sa.Column("reading_correct", sa.Integer(), nullable=False),
        sa.Column("reading_incorrect", sa.Integer(), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("interval_unit", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_srsstage_position"), "srsstage", ["position"], unique=True)
    op.create_table(
        "subject",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "object_type",
            sa.Enum("RADICAL", "KANJI", "VOCABULARY", name="subjecttype"),
            nullable=False,
        ),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("characters", sa.String(), nullable=True),
        sa.Column("meanings", sa.JSON(), nullable=True),
        sa.Column("readings", sa.JSON(), nullable=True),
        sa.Column("component_subject_ids", sa.JSON(), nullable=True),
        sa.Column("amalgamation_subject_ids", sa.JSON(), nullable=True),
        sa.Column("document_url", sa.String(), nullable=False),
        sa.Column("hidden_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subject_level"), "subject", ["level"], unique=False)
    op.create_index(
        op.f("ix_subject_object_type"), "subject", ["object_type"], unique=False
    )
    op.create_index(op.f("ix_subject_slug"), "subject", ["slug"], unique=False)
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wanikani_api_key", sa.String(), nullable=False),
        sa.Column("mcp_api_key", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("profile_url", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("subscription_active", sa.Boolean(), nullable=False),
        sa.Column("subscription_type", sa.String(), nullable=True),
        sa.Column("subscription_max_level_granted", sa.Integer(), nullable=True),
        sa.Column("subscription_period_ends_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_sync", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_level"), "user", ["level"], unique=False)
    op.create_index(op.f("ix_user_mcp_api_key"), "user", ["mcp_api_key"], unique=True)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=False)
    op.create_index(
        op.f("ix_user_wanikani_api_key"), "user", ["wanikani_api_key"], unique=True
    )
    op.create_table(
        "voiceactor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("gender", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "subject_type",
            sa.Enum("RADICAL", "KANJI", "VOCABULARY", name="subjecttype"),
            nullable=False,
        ),
        sa.Column("srs_stage", sa.Integer(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("passed_at", sa.DateTime(), nullable=True),
        sa.Column("burned_at", sa.DateTime(), nullable=True),
        sa.Column("available_at", sa.DateTime(), nullable=True),
        sa.Column("resurrected_at", sa.DateTime(), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_assignment_available_at"), "assignment", ["available_at"], unique=False
    )
    op.create_index(
        op.f("ix_assignment_srs_stage"), "assignment", ["srs_stage"], unique=False
    )
    op.create_index(
        op.f("ix_assignment_subject_id"), "assignment", ["subject_id"], unique=False
    )
    op.create_index(
        op.f("ix_assignment_user_id"), "assignment", ["user_id"], unique=False
    )
    op.create_table(
        "levelprogression",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("passed_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("abandoned_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_levelprogression_level"), "levelprogression", ["level"], unique=False
    )
    op.create_index(
        op.f("ix_levelprogression_user_id"),
        "levelprogression",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("assignment_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("starting_srs_stage", sa.Integer(), nullable=False),
        sa.Column("ending_srs_stage", sa.Integer(), nullable=False),
        sa.Column("incorrect_meaning_answers", sa.Integer(), nullable=False),
        sa.Column("incorrect_reading_answers", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_review_assignment_id"), "review", ["assignment_id"], unique=False
    )
    op.create_index(
        op.f("ix_review_subject_id"), "review", ["subject_id"], unique=False
    )
    op.create_index(op.f("ix_review_user_id"), "review", ["user_id"], unique=False)
    op.create_table(
        "reviewstatistic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "subject_type",
            sa.Enum("RADICAL", "KANJI", "VOCABULARY", name="subjecttype"),
            nullable=False,
        ),
        sa.Column("meaning_correct", sa.Integer(), nullable=False),
        sa.Column("meaning_incorrect", sa.Integer(), nullable=False),
        sa.Column("meaning_max_streak", sa.Integer(), nullable=False),
        sa.Column("meaning_current_streak", sa.Integer(), nullable=False),
        sa.Column("reading_correct", sa.Integer(), nullable=False),
        sa.Column("reading_incorrect", sa.Integer(), nullable=False),
        sa.Column("reading_max_streak", sa.Integer(), nullable=False),
        sa.Column("reading_current_streak", sa.Integer(), nullable=False),
        sa.Column("percentage_correct", sa.Integer(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reviewstatistic_subject_id"),
        "reviewstatistic",
        ["subject_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reviewstatistic_user_id"), "reviewstatistic", ["user_id"], unique=False
    )
    op.create_table(
        "studymaterial",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "subject_type",
            sa.Enum("RADICAL", "KANJI", "VOCABULARY", name="subjecttype"),
            nullable=False,
        ),
        sa.Column("meaning_note", sa.String(), nullable=True),
        sa.Column("reading_note", sa.String(), nullable=True),
        sa.Column("meaning_synonyms", sa.JSON(), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_studymaterial_subject_id"),
        "studymaterial",
        ["subject_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_studymaterial_user_id"), "studymaterial", ["user_id"], unique=False
    )
    op.create_table(
        "synclog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "sync_type",
            sa.Enum("FULL", "INCREMENTAL", "MANUAL", name="synctype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("SUCCESS", "ERROR", "IN_PROGRESS", name="syncstatus"),
            nullable=False,
        ),
        sa.Column("records_updated", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_synclog_user_id"), "synclog", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_synclog_user_id"), table_name="synclog")
    op.drop_table("synclog")
    op.drop_index(op.f("ix_studymaterial_user_id"), table_name="studymaterial")
    op.drop_index(op.f("ix_studymaterial_subject_id"), table_name="studymaterial")
    op.drop_table("studymaterial")
    op.drop_index(op.f("ix_reviewstatistic_user_id"), table_name="reviewstatistic")
    op.drop_index(op.f("ix_reviewstatistic_subject_id"), table_name="reviewstatistic")
    op.drop_table("reviewstatistic")
    op.drop_index(op.f("ix_review_user_id"), table_name="review")
    op.drop_index(op.f("ix_review_subject_id"), table_name="review")
    op.drop_index(op.f("ix_review_assignment_id"), table_name="review")
    op.drop_table("review")
    op.drop_index(op.f("ix_levelprogression_user_id"), table_name="levelprogression")
    op.drop_index(op.f("ix_levelprogression_level"), table_name="levelprogression")
    op.drop_table("levelprogression")
    op.drop_index(op.f("ix_assignment_user_id"), table_name="assignment")
    op.drop_index(op.f("ix_assignment_subject_id"), table_name="assignment")
    op.drop_index(op.f("ix_assignment_srs_stage"), table_name="assignment")
    op.drop_index(op.f("ix_assignment_available_at"), table_name="assignment")
    op.drop_table("assignment")
    op.drop_table("voiceactor")
    op.drop_index(op.f("ix_user_wanikani_api_key"), table_name="user")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_mcp_api_key"), table_name="user")
    op.drop_index(op.f("ix_user_level"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_subject_slug"), table_name="subject")
    op.drop_index(op.f("ix_subject_object_type"), table_name="subject")
    op.drop_index(op.f("ix_subject_level"), table_name="subject")
    op.drop_table("subject")
    op.drop_index(op.f("ix_srsstage_position"), table_name="srsstage")
    op.drop_table("srsstage")
    # ### end Alembic commands ###
