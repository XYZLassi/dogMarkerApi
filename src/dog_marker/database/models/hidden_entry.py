from sqlalchemy import Column, UUID, Integer, ForeignKey, UniqueConstraint

from ..base import Base


class HiddenEntry(Base):
    __tablename__ = "hidden_entries"
    __table_args__ = (
        UniqueConstraint("entry_id", "user_id", name="unique_entry_user"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(ForeignKey("entries.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
