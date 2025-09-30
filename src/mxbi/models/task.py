from enum import StrEnum, auto
from typing import TypeAlias

Feedback: TypeAlias = bool


class TaskEnum(StrEnum):
    IDEL = auto()
    ERROR = auto()
    GNGSiD_SIZE_REDUCTION_STAGE = auto()
    GNGSiD_VISUAL_DELAY_STAGE = auto()
    GNGSiD_DOUBLE_TOUCH_INTRODUCE = auto()
    GNGSiD_FINAL_STAGE = auto()
