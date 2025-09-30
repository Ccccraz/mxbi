from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import LevelID, MonkeyName

CONFIG_PATH = Path(__file__).parent / "config.json"


class DoubleTouchIntroduceStageParameters(BaseModel):
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
    visual_stimulus_delay: int
    silence_time_interval: int


class DoubleTouchIntroduceStageLeveledParameters(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: int
    min_stimulus_duration: int
    max_stimulus_duration: int
    single_touch_prob: float
    double_touch_prob: float


class DoubleTouchIntroduceStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: ScheduleCondition

    params: DoubleTouchIntroduceStageParameters
    levels_table: dict[LevelID, DoubleTouchIntroduceStageLeveledParameters]


class DoubleTouchIntroduceStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, DoubleTouchIntroduceStageConfig]


config = Configure(CONFIG_PATH, DoubleTouchIntroduceStageConfigs).value
