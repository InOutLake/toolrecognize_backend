"""create_scheme

Revision ID: 0ae8b373378ey
Revises:
Create Date: 2025-11-06 16:42:36.752918

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0ae8b373378e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Using uuid makes migration incopatible to many other databases
UUID_TYPE = postgresql.UUID

base = (
    sa.Column("id", UUID_TYPE, primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False),
    sa.PrimaryKeyConstraint("id"),
)


def upgrade() -> None:
    op.create_table(
        "employee",
        *base,
        sa.Column("first_name", sa.String(length=30), nullable=False),
        sa.Column("last_name", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=30), nullable=False),
    )

    op.create_table(
        "tool",
        *base,
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "location",
        *base,
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("address", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "kit",
        *base,
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
    )

    op.create_table(
        "session",
        *base,
        sa.Column("reciever_id", UUID_TYPE, nullable=False),
        sa.Column("giver_id", UUID_TYPE, nullable=False),
        sa.Column("location_id", UUID_TYPE, nullable=False),
        sa.Column("kit_id", UUID_TYPE, nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "ACTIVE", "COMPLETED", "CANCELLED", name="sessionstatus"
            ),
            nullable=False,
        ),
        sa.Column("given_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("given_image_key", sa.String(), nullable=True),
        sa.Column("returned_image_key", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["reciever_id"],
            ["employee.id"],
        ),
        sa.ForeignKeyConstraint(
            ["giver_id"],
            ["employee.id"],
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["location.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kit_id"],
            ["kit.id"],
        ),
    )

    op.create_table(
        "tools_in_kit",
        *base,
        sa.Column("tool_id", UUID_TYPE, nullable=False),
        sa.Column("kit_id", UUID_TYPE, nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("quantity > 0", name="check_kit_quantity_positive"),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tool.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kit_id"],
            ["kit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "session_tool",
        *base,
        sa.Column("tool_id", UUID_TYPE, nullable=False),
        sa.Column("session_id", UUID_TYPE, nullable=False),
        sa.Column("quantity_given", sa.Integer(), nullable=False),
        sa.Column("quantity_returned", sa.Integer(), nullable=False),
        sa.CheckConstraint("quantity_given >= 0", name="check_quantity_given_positive"),
        sa.CheckConstraint(
            "quantity_returned >= 0", name="check_quantity_returned_positive"
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tool.id"],
        ),
        sa.ForeignKeyConstraint(["session_id"], ["session.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("session_tool")
    op.drop_table("tools_in_kit")
    op.drop_table("session")
    op.drop_table("kit")
    op.drop_table("location")
    op.drop_table("tool")
    op.drop_table("employee")

    op.execute("DROP TYPE IF EXISTS sessionstatus")
