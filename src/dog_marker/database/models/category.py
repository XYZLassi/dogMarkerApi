from sqlalchemy import Column, String, Text

from ..base import Base
from ..schemas import Category


class CategoryDbModel(Base):
    __tablename__ = "categories"
    key: str = Column(String, primary_key=True)
    title: str = Column(String, nullable=False)
    description: str = Column(Text, nullable=True)

    def to_schema(self) -> Category:
        return Category(
            key=self.key,
            title=self.title,
            description=self.description,
        )
