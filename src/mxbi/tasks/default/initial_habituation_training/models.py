from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.tasks.GNGSiD.models import MonkeyName

CONFIG_PATH = Path(__file__).parent / "config.json"


class DetectStageParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    stay_duration: int

    # reward config
    reward_duration: int


class DetectStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    params: DetectStageParams


class DetectStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, DetectStageConfig]


class TrialData(BaseModel):
    animal: MonkeyName
    trial_id: int
    trial_start_time: float
    trial_end_time: float

    stay_duration: float
    rewards: dict[float, int]


class DataToShow(BaseModel):
    name: str
    id: int
    dur: str
    rewards: int


config = Configure(CONFIG_PATH, DetectStageConfigs).value
