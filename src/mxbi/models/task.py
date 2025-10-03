from enum import StrEnum, auto
from typing import TypeAlias

Feedback: TypeAlias = bool


class TaskEnum(StrEnum):
    IDEL = auto()
    ERROR = auto()
    GNGSiD_SIZE_REDUCTION_STAGE = auto()
    GNGSiD_DETECT_STAGE = auto()
    GNGSiD_DISCRIMINATE_STAGE = auto()
