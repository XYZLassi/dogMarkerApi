"""Add EntryImageDbModel

Revision ID: 75802f69ee1c
Revises: 289869099d4b
Create Date: 2024-03-18 21:28:21.607663

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "75802f69ee1c"
down_revision: Union[str, None] = "289869099d4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "entry_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entry_id", sa.UUID(), nullable=False),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("image_delete_url", sa.String(), nullable=True),
        sa.Column("create_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["entry_id"], ["entries.id"], name=op.f("fk_entry_images_entry_id_entries"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entry_images")),
    )
    op.drop_column("entries", "image_delete_url")
    op.drop_column("entries", "image_path")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("entries", sa.Column("image_path", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("entries", sa.Column("image_delete_url", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table("entry_images")
    # ### end Alembic commands ###