"""Create scientometrics metric tables.

Revision ID: e132bccf90e5
Revises:
Create Date: 2025-12-14 14:39:51.535192
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e132bccf90e5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scim_user_metric",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Text, sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("external_id", sa.Text),
        sa.Column("external_url", sa.Text),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("extras", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("user_id", "source", name="uq_scim_user_metric"),
    )

    op.create_table(
        "scim_dataset_metric",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("package_id", sa.Text, sa.ForeignKey("package.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("external_id", sa.Text),
        sa.Column("external_url", sa.Text),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'pending'")),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("extras", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("package_id", "source", name="uq_scim_dataset_metric"),
    )


def downgrade():
    op.drop_table("scim_dataset_metric")
    op.drop_table("scim_user_metric")
