from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import MonkeyName, LevelID

CONFIG_PATH = Path(__file__).parent / "config.json"


class stimulus_config(BaseModel):
    stimulus_freq_high: int
    stimulus_freq_high_duration: int
    stimulus_freq_low: int
    stimulus_freq_low_duration: int


class DiscriminateStageParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    # visual stimulation config
    stimulation_size: int
    visual_stimulus_delay: int

    # audio stimulation config
    min_stimulus_duration: int
    max_stimulus_duration: int
    silence_time_interval: int
    stimulus_configs: list[stimulus_config]
    stimulus_interval: int

    # trial lifecycle
    time_out: int
    inter_trial_interval: int

    # reward config
    reward_duration: int
    reward_delay: int

    attention_duration: int


class DiscriminateStageLeveledParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: int

    go_task_prob: float
    nogo_task_prob: float


class DiscriminateStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: ScheduleCondition

    params: DiscriminateStageParams
    levels_table: dict[LevelID, DiscriminateStageLeveledParams]


class DiscriminateStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, DiscriminateStageConfig]


config = Configure(CONFIG_PATH, DiscriminateStageConfigs).value
