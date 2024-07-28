from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import declared_attr, relationship, Mapped

from dog_marker.database.base import Base

from ..category import CategoryDbModel


class CategoryMixin:

    @declared_attr
    def categories(self) -> Mapped[list[CategoryDbModel]]:
        if not hasattr(self, "__tablename__"):
            raise NotImplementedError("You must declare a __tablename__ attribute")

        # noinspection PyUnresolvedReferences
        table_name = self.__tablename__
        association_table = Table(
            f"{table_name}_categories_associations",  # type: ignore
            Base.metadata,
            Column("item_id", ForeignKey(f"{table_name}.id", ondelete="CASCADE"), nullable=False),  # type: ignore
            Column("category_key", ForeignKey("categories.key", ondelete="CASCADE"), nullable=False),
        )

        # noinspection PyTypeChecker
        return relationship("CategoryDbModel", lazy="dynamic", secondary=association_table)  # type: ignore

    def append_category(self, category: CategoryDbModel):
        self.categories.append(category)

    def append_categories(self, *categories: CategoryDbModel):
        for cat in categories:
            self.append_category(cat)

    def clear_categories(self):
        for cat in self.categories:
            self.categories.remove(cat)
