"""sessionstatus

Revision ID: 882ca76691b0
Revises: 789691eb40ea
Create Date: 2025-10-01 00:42:33.715839

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "882ca76691b0"
down_revision: Union[str, Sequence[str], None] = "789691eb40ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SESSION_STATUS_ENUM_NAME = "sessionstatus"
SESSION_STATUS_VALUES = [
    "open_waiting_for_aproval",
    "opened",
    "close_waiting_for_aproval",
    "closed",
]


def upgrade():
    session_status_enum = sa.Enum(*SESSION_STATUS_VALUES, name=SESSION_STATUS_ENUM_NAME)
    session_status_enum.create(op.get_bind())

    op.alter_column(
        "session",
        "status",
        existing_type=sa.String(),
        type_=session_status_enum,
        nullable=False,
        postgresql_using="status::text::sessionstatus",
    )


def downgrade():
    op.alter_column(
        "session",
        "status",
        existing_type=sa.Enum(*SESSION_STATUS_VALUES, name=SESSION_STATUS_ENUM_NAME),
        type_=sa.String(),
        nullable=False,
        postgresql_using="status::text",
    )

    session_status_enum = sa.Enum(*SESSION_STATUS_VALUES, name=SESSION_STATUS_ENUM_NAME)
    session_status_enum.drop(op.get_bind())
