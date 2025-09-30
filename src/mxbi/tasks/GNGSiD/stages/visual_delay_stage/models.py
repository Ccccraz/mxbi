from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import LevelID, MonkeyName

CONFIG_PATH = Path(__file__).parent / "config.json"


class VisualDelayStageParameters(BaseModel):
    model_config = ConfigDict(frozen=True)

    stimulation_size: int
    stimulus_duration_total: int
    reward_delay: int
    stimulus_frequency: int
    time_out: int
    stimulus_duration_single: int
    stimulus_interval: int
    reward_duration: int
    inter_trial_interval: int


class VisualDelayStageLeveledParameters(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: int
    min_stimulus_duration: int
    max_stimulus_duration: int
    visual_stimulus_delay: int


class VisualDelayStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: ScheduleCondition

    params: VisualDelayStageParameters
    levels_table: dict[LevelID, VisualDelayStageLeveledParameters]


class VisualDelayStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, VisualDelayStageConfig]


config = Configure(CONFIG_PATH, VisualDelayStageConfigs).value
