from datetime import datetime

from sqlalchemy import Column, UUID, ForeignKey, PrimaryKeyConstraint, DateTime, func

from ..base import Base


class HiddenEntry(Base):
    __tablename__ = "hidden_entries"
    __table_args__ = (PrimaryKeyConstraint("entry_id", "user_id"),)

    entry_id: UUID = Column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)
    user_id: UUID = Column(UUID(as_uuid=True), nullable=False)  # type: ignore

    create_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    update_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.now,
    )
