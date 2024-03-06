import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    Double,
    DateTime,
    func,
    Boolean,
    CheckConstraint,
)

from ..base import Base


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = (
        CheckConstraint(
            "longitude >= -180 and longitude <= 180 ", name="check_longitude"
        ),
        CheckConstraint(
            "latitude >= -90 and latitude <= 90 ", name="check_latitude"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mark_to_delete = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    longitude = Column(Double, nullable=False)
    latitude = Column(Double, nullable=False)
    create_date = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    update_date = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.now,
    )
