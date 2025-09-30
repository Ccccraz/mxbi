from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import LevelID, MonkeyName

CONFIG_PATH = Path(__file__).parent / "config.json"


class SizeReductionStageParameters(BaseModel):
    model_config = ConfigDict(frozen=True)

    stimulus_frequency: int
    time_out: int
    stimulus_duration_total: int
    stimulus_duration_single: int
    stimulus_interval: int
    reward_duration: int
    inter_trial_interval: int


class SizeReductionStageLeveledParameters(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: int
    stimulation_size: int
    reward_delay: int


class SizeReductionStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: ScheduleCondition

    params: SizeReductionStageParameters
    levels_table: dict[LevelID, SizeReductionStageLeveledParameters]


class SizeReductionStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, SizeReductionStageConfig]


config = Configure(CONFIG_PATH, SizeReductionStageConfigs).value
