"""init

Revision ID: 789691eb40ea
Revises:
Create Date: 2025-09-25 18:37:19.849792

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "789691eb40ea"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employee",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "tool",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "kit",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "location",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(30), nullable=False),
        sa.Column("address", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "session",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reciever_id", sa.Integer, sa.ForeignKey("employee.id")),
        sa.Column("giver_id", sa.Integer, sa.ForeignKey("employee.id")),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("location.id")),
        sa.Column("kit_id", sa.Integer, sa.ForeignKey("kit.id")),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("given_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("given_image_key", sa.String(), nullable=True),
        sa.Column("returned_image_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "session_tool",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tool_id", sa.Integer, sa.ForeignKey("tool.id")),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("session.id")),
        sa.Column("quantity_given", sa.Integer, nullable=False),
        sa.Column("quantity_returned", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("quantity_given >= 0", name="check_quantity_given_positive"),
        sa.CheckConstraint(
            "quantity_returned >= 0", name="check_quantity_returned_positive"
        ),
    )

    op.create_table(
        "tools_in_kit",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tool_id", sa.Integer, sa.ForeignKey("tool.id")),
        sa.Column("kit_id", sa.Integer, sa.ForeignKey("kit.id")),
        sa.Column("quantity", sa.Integer, nullable=False, default=1),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("quantity > 0", name="check_kit_quantity_positive"),
    )


def downgrade() -> None:
    op.drop_table("tools_in_kit")
    op.drop_table("session_tool")
    op.drop_table("session")
    op.drop_table("location")
    op.drop_table("kit")
    op.drop_table("tool")
    op.drop_table("employee")
