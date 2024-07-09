from __future__ import annotations

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
    CheckConstraint,
    Index,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped

from .hidden_entry import HiddenEntry
from .mixin.category_mixin import CategoryMixin
from ..base import Base


class EntryImageDbModel(Base):
    __tablename__ = "entry_images"
    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False)
    entry: Mapped[EntryDbModel] = relationship("EntryDbModel", back_populates="image_infos")

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
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    hidden_entries: Mapped[list[HiddenEntry]] = relationship("HiddenEntry", cascade="all,delete")

    image_infos: Mapped[list[EntryImageDbModel]] = relationship(
        "EntryImageDbModel", order_by="desc(EntryImageDbModel.id)", back_populates="entry"
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
    def is_deleted(self) -> bool:
        for h_entry in self.hidden_entries:
            if h_entry.user_id == self.user_id and h_entry.entry_id == self.id:
                return True
        return False

    @property
    def image_path(self) -> str | None:
        return self.image_infos[0].image_path if self.image_infos else None

    @property
    def image_delete_url(self) -> str | None:
        return self.image_infos[0].image_delete_url if self.image_infos else None

    @staticmethod  # Todo: Right Methode in sqlalchemey
    def calc_distance(longitude, latitude):
        d_lat = EntryDbModel.latitude - latitude
        d_lon = EntryDbModel.longitude - longitude

        a = func.pow(func.sin(d_lat / 2.0), 2) + func.pow(func.sin(d_lon / 2.0), 2) * func.cos(latitude) * func.cos(
            EntryDbModel.latitude
        )
        dist = 6378.388 * 2.0 * func.atan2(func.sqrt(a), func.sqrt(1.0 - a))

        return dist
