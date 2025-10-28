from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("organizer_email", sa.Text(), nullable=False),
        sa.Column("budget", sa.Integer(), nullable=True),
        sa.Column("reveal_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("allow_household", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("join_pin", sa.String(length=6), nullable=False),
        sa.Column("join_token", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("household", sa.Text(), nullable=True),
        sa.Column("interests", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("nogos", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("is_organizer", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("group_id", "email"),
    )

    op.create_table(
        "exclusions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE")),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE")),
        sa.Column("excluded_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE")),
        sa.UniqueConstraint("member_id", "excluded_member_id"),
    )

    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE")),
        sa.Column("giver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE")),
        sa.Column("receiver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE")),
        sa.UniqueConstraint("group_id", "giver_id"),
        sa.UniqueConstraint("group_id", "receiver_id"),
    )

    op.create_table(
        "anon_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE")),
        sa.Column("from_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="SET NULL")),
        sa.Column("to_member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="SET NULL")),
        sa.Column("direction", sa.String(length=1), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("anon_messages")
    op.drop_table("assignments")
    op.drop_table("exclusions")
    op.drop_table("members")
    op.drop_table("groups")
