from typing import TYPE_CHECKING, Final
from random import choices

from mxbi.data_logger import DataLogger
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import Result
from mxbi.tasks.GNGSiD.stages.double_touch_introduce_stage.models import config
from mxbi.tasks.GNGSiD.tasks.detect_double_touch.models import (
    TrialConfig as DoubleTouchTrialConfig,
)
from mxbi.tasks.GNGSiD.tasks.detect_double_touch.scene import (
    GNGSiDDetectDoubleTouchScene,
)
from mxbi.tasks.GNGSiD.tasks.detect_single_touch.models import (
    TrialConfig as WithoutTouchToRewardTrialConfig,
)
from mxbi.tasks.GNGSiD.tasks.detect_single_touch.scene import (
    GNGSiDDetectSingleTouchScene,
)
from mxbi.utils.logger import logger

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.models.task import Feedback
    from mxbi.theater import Theater


class GNGSiDDoubleTouchIntroduceStage:
    STAGE_NAME: Final[str] = "GNGSiD_double_touch_introduce_stage"

    def __init__(
        self,
        theater: "Theater",
        session_state: "SessionState",
        animal_state: "AnimalState",
    ) -> None:
        self._session_state = session_state
        self._animal_state = animal_state

        self._stage_config = config.root["default"]
        _fixed_config = self._stage_config.params
        _levels_config = self._stage_config.levels_table[animal_state.level]

        is_double_touch = choices(
            [False, True],
            weights=[
                _levels_config.single_touch_prob,
                _levels_config.double_touch_prob,
            ],
        )[0]

        if is_double_touch:
            _config = DoubleTouchTrialConfig(
                **{**_fixed_config.model_dump(), **_levels_config.model_dump()}
            )
            self._task = GNGSiDDetectDoubleTouchScene(
                theater, animal_state, session_state.session_config.screen_type, _config
            )
        else:
            _config = WithoutTouchToRewardTrialConfig(
                **{**_fixed_config.model_dump(), **_levels_config.model_dump()}
            )
            self._task = GNGSiDDetectSingleTouchScene(
                theater, animal_state, session_state.session_config.screen_type, _config
            )

        self._data_logger = DataLogger(
            self._session_state, self._animal_state.name, self.STAGE_NAME
        )

    def start(self) -> "Feedback":
        trial_data = self._task.start()
        self._data_logger.save_jsonl(trial_data.model_dump())

        feedback = self._handle_result(trial_data.result)
        logger.debug(
            f"Size Reduction Stage: "
            f"session_id={self._session_state.session_id}, "
            f"animal_name={self._animal_state.name}, "
            f"animal_level={self._animal_state.level}, "
            f"state_name={self.STAGE_NAME}, "
            f"result={trial_data}, "
            f"feedback={feedback}"
        )

        return feedback

    def _handle_result(self, result: "Result") -> "Feedback":
        feedback = False
        match result:
            case Result.CORRECT:
                feedback = True
            case Result.INCORRECT:
                feedback = False
            case Result.TIMEOUT:
                feedback = False
            case Result.CANCEL:
                feedback = False

        return feedback

    def quit(self) -> None:
        self._task.cancle()

    def on_idle(self) -> None:
        self._task.cancle()

    def on_return(self) -> None:
        self._task.cancle()

    @property
    def condition(self) -> "ScheduleCondition | None":
        self._stage_config.condition
