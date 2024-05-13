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
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from dog_marker.database.schemas import Entry, WarningLevel
from ..base import Base

from .mixin.category_mixin import CategoryMixin


class EntryImageDbModel(Base):
    __tablename__ = "entry_images"
    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)
    entry = relationship("EntryDbModel", back_populates="image_info")

    image_path = Column(String, nullable=True)
    image_delete_url = Column(String, nullable=True)

    create_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )


class EntryDbModel(Base, CategoryMixin):
    __tablename__ = "entries"
    __table_args__ = (
        Index("ix_entries_coordinates", "longitude", "latitude"),
        CheckConstraint("warning_level >= 0 and warning_level <= 2 ", name="check_warning_level"),
        CheckConstraint("longitude >= -180 and longitude <= 180 ", name="check_longitude"),
        CheckConstraint("latitude >= -90 and latitude <= 90 ", name="check_latitude"),
        CheckConstraint("update_date >= create_date ", name="check_update_time"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mark_to_delete = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    image_info = relationship(
        "EntryImageDbModel", uselist=False, order_by="desc(EntryImageDbModel.id)", back_populates="entry"
    )

    warning_level = Column(Integer, nullable=False, default=0, server_default="0")

    longitude = Column(Double, nullable=False)
    latitude = Column(Double, nullable=False)
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

    @property
    def image_path(self) -> str | None:
        return self.image_info.image_path if self.image_info else None

    @property
    def image_delete_url(self) -> str | None:
        return self.image_info.image_delete_url if self.image_info else None

    def to_schema(self) -> Entry:
        return Entry(
            id=self.id,
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            image_path=self.image_path,
            image_delete_url=self.image_delete_url,
            warning_level=WarningLevel(self.warning_level),
            longitude=self.longitude,
            latitude=self.latitude,
            categories=[category.to_schema() for category in self.categories],
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
