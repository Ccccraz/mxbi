from typing import TYPE_CHECKING, Final
from random import choices, choice, randint

from mxbi.data_logger import DataLogger
from mxbi.models.animal import ScheduleCondition
from mxbi.tasks.GNGSiD.models import Result
from mxbi.tasks.GNGSiD.stages.discriminate_stage.discriminate_stage_models import config
from mxbi.tasks.GNGSiD.tasks.discriminate.discriminate_models import TrialConfig
from mxbi.tasks.GNGSiD.tasks.discriminate.discriminate_scene import (
    GNGSiDDiscriminateScene,
)
from mxbi.utils.logger import logger
from mxbi.utils.audio_control import get_amp_value

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.models.task import Feedback
    from mxbi.theater import Theater


class GNGSiDDiscriminateStage:
    STAGE_NAME: Final[str] = "GNGSiD_DISCRIMINATE_STAGE"

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

        _stimulus_config = choice(_fixed_config.stimulus_configs)
        _stimulus_duration = randint(
            _fixed_config.min_stimulus_duration, _fixed_config.max_stimulus_duration
        )

        _is_go = choices(
            [True, False],
            weights=[_levels_config.go_task_prob, _levels_config.nogo_task_prob],
        )[0]

        _high_master_amp, _high_digital_amp = self._prepare_stimulus_intensity(
            animal_state.name, _stimulus_config.stimulus_freq_high
        )
        _low_master_amp, _low_digital_amp = self._prepare_stimulus_intensity(
            animal_state.name, _stimulus_config.stimulus_freq_low
        )

        _config = TrialConfig(
            level=_levels_config.level,
            stimulation_size=_fixed_config.stimulation_size,
            stimulus_duration=_stimulus_duration,
            time_out=_fixed_config.time_out,
            inter_trial_interval=_fixed_config.inter_trial_interval,
            reward_duration=_fixed_config.reward_duration,
            reward_delay=_fixed_config.reward_delay,
            go=_is_go,
            visual_stimulus_delay=_fixed_config.visual_stimulus_delay,
            attention_duration=_fixed_config.attention_duration,
            stimulus_freq_low=_stimulus_config.stimulus_freq_low,
            stimulus_freq_low_duration=_stimulus_config.stimulus_freq_low_duration,
            stimulus_freq_low_master_amp=_low_master_amp,
            stimulus_freq_low_digital_amp=_low_digital_amp,
            stimulus_freq_high=_stimulus_config.stimulus_freq_high,
            stimulus_freq_high_duration=_stimulus_config.stimulus_freq_high_duration,
            stimulus_freq_high_master_amp=_high_master_amp,
            stimulus_freq_high_digital_amp=_high_digital_amp,
            stimulus_interval=_fixed_config.stimulus_interval,
        )

        self._task = GNGSiDDiscriminateScene(
            theater,
            session_state.session_config,
            animal_state,
            session_state.session_config.screen_type,
            _config,
        )

        self._data_logger = DataLogger(
            self._session_state, self._animal_state.name, self.STAGE_NAME
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

    def _prepare_stimulus_intensity(self, monkey: str, frequency: int):
        bt = choice(([[10, 30], [50, 70]])) if monkey == "wolfgang" else []
        at = [80, 80, 80] if monkey == "wolfgang" else [80, 80, 80]
        intensity_options = at * 10 + bt

        stimulus_intensity = choice(intensity_options)

        return get_amp_value(frequency, stimulus_intensity)
