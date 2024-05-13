from __future__ import annotations
from enum import IntEnum
from typing import Literal

warning_levels = Literal["information", "warning", "danger"]


class WarningLevel(IntEnum):
    information = 0
    warning = 1
    danger = 2

    def to_literal(self) -> warning_levels:
        if self == WarningLevel.information:
            return "information"
        elif self == WarningLevel.warning:
            return "warning"
        elif self == WarningLevel.danger:
            return "danger"

    @classmethod
    def from_(cls, value: WarningLevel | warning_levels | None) -> WarningLevel:
        if value is None:
            return WarningLevel.information

        if isinstance(value, WarningLevel):
            return value

        return cls[value]
