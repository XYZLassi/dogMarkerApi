import uuid
from datetime import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, Query

from ..models import Entry, HiddenEntry
from ...dtypes.coordinate import Coordinate


def calc_distance(longitude, latitude):
    d_lat = Entry.latitude - latitude
    d_lon = Entry.longitude - longitude

    a = func.pow(func.sin(d_lat / 2.0), 2) + func.pow(func.sin(d_lon / 2.0), 2) * func.cos(latitude) * func.cos(
        Entry.latitude
    )
    dist = 6378.388 * 2.0 * func.atan2(func.sqrt(a), func.sqrt(1.0 - a))

    return dist


def get_entries(
    db: Session,
    user_id: uuid.UUID | None = None,
    owner_id: uuid.UUID | None = None,
    coordinate: Coordinate | None = None,  # Todo: Dataclass
    skip: int | None = None,
    limit: int | None = None,
) -> list[Entry]:
    query: Query[Entry] = db.query(Entry)
    query = query.filter_by(mark_to_delete=False)

    if owner_id is not None:
        query = query.filter(Entry.user_id == owner_id)
    elif user_id is not None:
        query = query.join(
            HiddenEntry,
            onclause=and_(
                HiddenEntry.entry_id == Entry.id,
                HiddenEntry.user_id == user_id,
            ),
            isouter=True,
        )
        query = query.filter(HiddenEntry.entry_id == None)  # noqa: E711

    if coordinate:
        query = query.order_by(calc_distance(coordinate.longitude, coordinate.latitude))

    if skip is not None:
        query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    return query.all()


def create_entry(
    db: Session,
    user_id: uuid.UUID,
    title: str,
    longitude: float,
    latitude: float,
    id: uuid.UUID | None = None,
    description: str | None = None,
    image_path: str | None = None,
    create_date: datetime | None = None,
) -> Entry:
    new_entry = Entry(
        id=id,
        user_id=user_id,
        title=title,
        description=description,
        image_path=image_path,
        longitude=longitude,
        latitude=latitude,
        create_date=create_date,
    )

    db.add(new_entry)
    db.commit()

    return new_entry


def get_entry(db: Session, entry_id: uuid.UUID) -> Entry | None:
    return db.query(Entry).filter_by(id=entry_id, mark_to_delete=False).first()


def delete_entry(db: Session, entry_id: uuid.UUID, user_id=uuid.UUID) -> None:
    entry = get_entry(db, entry_id)
    if not entry:
        return None

    if entry.user_id == user_id:
        entry.mark_to_delete = True
        db.commit()
        return None

    hidden_entry = db.query(HiddenEntry).filter_by(entry_id=entry.id, user_id=user_id).first()

    if hidden_entry:
        return None

    hidden_entry = HiddenEntry(entry_id=entry.id, user_id=user_id)
    db.add(hidden_entry)
    db.commit()

    return None


def update_entry(
    db: Session,
    entry_id: uuid.UUID,
    title: str,
    longitude: float,
    latitude: float,
    description: str | None = None,
    image_path: str | None = None,
) -> Entry | None:
    entry = get_entry(db, entry_id)

    if not entry:
        return None

    entry.title = title
    entry.longitude = longitude
    entry.latitude = latitude
    entry.description = description
    entry.image_path = image_path
    db.commit()

    return entry
