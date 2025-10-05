from enum import StrEnum, auto

from pydantic import BaseModel, ConfigDict, Field

from mxbi.models.animal import AnimalConfig, AnimalOptions
from mxbi.models.reward import RewardEnum
from mxbi.utils.detect_platform import Platform


class ScreenTypeEnum(StrEnum):
    DEFAULT = auto()


class ScreenConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: ScreenTypeEnum = ScreenTypeEnum.DEFAULT
    width: int = 1024
    height: int = 600


class SessionConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    experimenter: str = ""
    xbi_id: str = ""
    comments: str = ""
    reward_type: RewardEnum = RewardEnum.AGUM_ONE_FIFTH
    platform: Platform = Platform.RASPBERRY
    RFID: bool = True
    screen_type: ScreenConfig = Field(default_factory=ScreenConfig)
    animals: dict[str, AnimalConfig] = Field(default_factory=dict)


class SessionState(BaseModel):
    session_id: int = 0
    start_time: float = Field(default=0.0, frozen=True)
    end_time: float = 0.0

    session_config: SessionConfig = Field(default_factory=SessionConfig, frozen=True)


class SessionOptions(BaseModel):
    model_config = ConfigDict(frozen=True)

    experimenter: list[str]
    xbi_id: list[str]
    reward_type: list[RewardEnum] = Field(default_factory=lambda: list(RewardEnum))
    platform: list[Platform] = Field(default_factory=lambda: list(Platform))
    RFID: list[bool] = Field(default_factory=lambda: [False, True])
    screen_type: dict[ScreenTypeEnum, ScreenConfig] = Field(
        default_factory=lambda: dict({ScreenTypeEnum.DEFAULT: ScreenConfig()})
    )
    animal: AnimalOptions
