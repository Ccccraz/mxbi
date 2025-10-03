from typing import TYPE_CHECKING, Final

from mxbi.data_logger import DataLogger
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import Result
from mxbi.tasks.GNGSiD.stages.size_reduction_stage.size_reduction_models import config
from mxbi.tasks.GNGSiD.tasks.touch.touch_models import TrialConfig
from mxbi.tasks.GNGSiD.tasks.touch.touch_scene import GNGSiDTouchScene
from mxbi.utils.logger import logger

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.models.task import Feedback
    from mxbi.theater import Theater


class SizeReductionStage:
    STAGE_NAME: Final[str] = "GNGSiD_SIZE_REDUCTION_STAGE"

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

        _config = TrialConfig(
            **{**_fixed_config.model_dump(), **_levels_config.model_dump()}
        )

        self._data_logger = DataLogger(
            self._session_state, self._animal_state.name, self.STAGE_NAME
        )

        self._task = GNGSiDTouchScene(
            theater,
            animal_state,
            session_state.session_config.screen_type,
            _config,
        )

    def start(self) -> "Feedback":
        trial_data = self._task.start()
        self._data_logger.save_jsonl(trial_data.model_dump())

        feedback = self._handle_result(trial_data.result)
        logger.debug(
            f"{self.STAGE_NAME}: "
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
        return self._stage_config.condition
