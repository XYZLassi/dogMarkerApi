from pydantic import BaseModel


class Category(BaseModel):
    key: str
    title: str
    description: str | None
