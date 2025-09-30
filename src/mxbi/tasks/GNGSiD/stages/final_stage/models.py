from pathlib import Path

from pydantic import BaseModel, ConfigDict, RootModel

from mxbi.config import Configure
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import MonkeyName
from mxbi.tasks.GNGSiD.tasks.frequency_discrimination_double_touch.models import TrialConfig

CONFIG_PATH = Path(__file__).parent / "config.json"


class FinalStageParameters(TrialConfig):
    single_touch_prob: float
    double_touch_prob: float


class FinalStageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: ScheduleCondition

    params: FinalStageParameters


class FinalStageConfigs(RootModel):
    model_config = ConfigDict(frozen=True)

    root: dict[MonkeyName, FinalStageConfig]


config = Configure(CONFIG_PATH, FinalStageConfigs).value
