"""Add: entries.warning_level

Revision ID: fea451ae3e06
Revises: 75802f69ee1c
Create Date: 2024-05-13 11:33:29.564812

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fea451ae3e06"
down_revision: Union[str, None] = "75802f69ee1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("entries", sa.Column("warning_level", sa.Integer(), server_default="0", nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("entries", "warning_level")
    # ### end Alembic commands ###