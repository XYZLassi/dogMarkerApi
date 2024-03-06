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
    Index,
)

from .schemas.entry import Entry
from ..base import Base


class EntryDbModel(Base):
    __tablename__ = "entries"
    __table_args__ = (
        Index("ix_entries_coordinates", "longitude", "latitude"),
        CheckConstraint("longitude >= -180 and longitude <= 180 ", name="check_longitude"),
        CheckConstraint("latitude >= -90 and latitude <= 90 ", name="check_latitude"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mark_to_delete = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
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

    def to_schema(self) -> Entry:
        return Entry(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            image_path=self.image_path,
            longitude=self.longitude,
            latitude=self.latitude,
            create_date=self.create_date,
            update_date=self.update_date,
        )

    @staticmethod  # Todo: Right Methode in sqlalchemey
    def calc_distance(longitude, latitude):
        d_lat = EntryDbModel.latitude - latitude
        d_lon = EntryDbModel.longitude - longitude

        a = func.pow(func.sin(d_lat / 2.0), 2) + func.pow(func.sin(d_lon / 2.0), 2) * func.cos(latitude) * func.cos(
            EntryDbModel.latitude
        )
        dist = 6378.388 * 2.0 * func.atan2(func.sqrt(a), func.sqrt(1.0 - a))

        return dist
