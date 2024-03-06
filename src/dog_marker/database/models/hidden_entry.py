from sqlalchemy import Column, UUID, ForeignKey, PrimaryKeyConstraint

from ..base import Base


class HiddenEntry(Base):
    __tablename__ = "hidden_entries"
    __table_args__ = (PrimaryKeyConstraint("entry_id", "user_id"),)

    entry_id = Column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
