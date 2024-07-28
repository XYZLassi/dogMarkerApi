import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, ForeignKey, String, DateTime, func

from ..base import Base


class EntryCommentDbModel(Base):
    __tablename__ = "entry_comments"
    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    entry_id: uuid.UUID = Column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)

    comment = Column(String, nullable=True)

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
        onupdate=datetime.utcnow,
    )
