"""Add: EntryDbModel.mark_to_delete

Revision ID: e7493efb103b
Revises: 8234f673b3d3
Create Date: 2024-07-10 22:04:34.611905

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7493efb103b"
down_revision: Union[str, None] = "8234f673b3d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("entries", sa.Column("mark_to_delete", sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("entries", "mark_to_delete")
    # ### end Alembic commands ###
