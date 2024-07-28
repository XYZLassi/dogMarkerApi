from uuid import UUID

from pydantic import BaseModel, Field


class EntryLikeSchema(BaseModel):
    id: UUID
    entry_id: UUID
    comment: str | None


class CreateEntryLikeSchema(BaseModel):
    entry_id: UUID
    comment: str | None = Field(None)
