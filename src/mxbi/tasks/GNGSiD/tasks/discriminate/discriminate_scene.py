from concurrent.futures import Future
from datetime import datetime
from math import ceil
from tkinter import CENTER, Canvas, Event
from typing import TYPE_CHECKING, Final

from mxbi.models.session import ScreenConfig
from mxbi.tasks.GNGSiD.models import Result, TouchEvent
from mxbi.tasks.GNGSiD.tasks.discriminate.discriminate_models import TrialConfig, TrialData
from mxbi.tasks.GNGSiD.tasks.utils.targets import DiscriminateTarget
from mxbi.utils.aplayer import ToneConfig

if TYPE_CHECKING:
    from numpy import int16
    from numpy.typing import NDArray

    from mxbi.models.animal import AnimalState
    from mxbi.theater import Theater


class GNGSiDDiscriminateScene:
    def __init__(
        self,
        theater: "Theater",
        animal_state: "AnimalState",
        screen_tupe: "ScreenConfig",
        trial_config: "TrialConfig",
    ) -> None:
        self._theater: Final[Theater] = theater
        self._animal_state: Final[AnimalState] = animal_state
        self._screen_type: Final[ScreenConfig] = screen_tupe
        self._trial_config: Final[TrialConfig] = trial_config
        self._is_go_trial: bool = bool(trial_config.go)

        self._attentation_stimulus = self._prepare_stimulus(
            trial_config.stimulus_freq_low,
            trial_config.stimulus_freq_low_duration,
            0,
            trial_config.stimulus_interval,
            trial_config.attention_duration,
        )
        if self._is_go_trial:
            self._stimulus = self._prepare_stimulus(
                self._trial_config.stimulus_freq_low,
                self._trial_config.stimulus_freq_low_duration,
                self._trial_config.stimulus_freq_high,
                self._trial_config.stimulus_freq_high_duration,
                self._trial_config.stimulus_duration,
            )
        else:
            self._stimulus = self._prepare_stimulus(
                self._trial_config.stimulus_freq_low,
                self._trial_config.stimulus_freq_low_duration,
                0,
                self._trial_config.stimulus_interval,
                self._trial_config.stimulus_duration,
            )

        self._on_trial_start()

    # region public api
    def start(self) -> TrialData:
        self._theater.mainloop()
        return self._data

    def cancle(self) -> None:
        self._data.result = Result.CANCEL
        self._on_trial_end()

    # endregion

    # region lifecycle
    def _on_trial_start(self) -> None:
        self._create_view()
        self._init_data()
        self._bind_first_stage()

    def _on_inter_trial(self) -> None:
        self._backgroud.after(
            self._trial_config.inter_trial_interval, self._on_trial_end
        )

    def _on_trial_end(self) -> None:
        self._backgroud.destroy()
        self._theater.root.quit()

    # endregion

    # region views
    def _create_view(self) -> None:
        self._create_background()
        self._create_target()

    def _create_background(self) -> None:
        self._backgroud = Canvas(
            self._theater.root,
            bg="black",
            width=self._screen_type.width,
            height=self._screen_type.height,
            highlightthickness=0,
        )
        self._backgroud.place(relx=0.5, rely=0.5, anchor="center")

    def _create_target(self) -> None:
        xshift = 240
        xcenter = self._screen_type.width * 0.5 + xshift
        ycenter = self._screen_type.height * 0.5

        self._trigger_canvas = DiscriminateTarget(
            self._backgroud, self._trial_config.stimulation_size
        )
        self._trigger_canvas.place(x=xcenter, y=ycenter, anchor="center")

    def _create_wrong_view(self) -> None:
        self._trigger_canvas = Canvas(
            self._backgroud,
            bg="grey",
            width=self._screen_type.width,
            height=self._screen_type.height,
        )
        self._trigger_canvas.place(relx=0.5, rely=0.5, anchor=CENTER)

    # endregion

    # region event binding
    def _bind_first_stage(self) -> None:
        self._backgroud.focus_set()
        self._backgroud.bind("<r>", lambda e: self._give_reward())
        self._trigger_canvas.bind("<ButtonPress>", self._on_first_touched)
        self._trigger_canvas.after(self._trial_config.time_out, self._on_timeout)

    def _bind_second_stage(self) -> None:
        self._trigger_canvas.bind("<ButtonPress>", self._on_second_touched)
        timeout_handler = self._on_incorrect if self._is_go_trial else self._on_correct
        self._trigger_canvas.after(
            self._trial_config.stimulus_duration, timeout_handler
        )

    # endregion

    # region event handlers
    def _on_first_touched(self, event: Event) -> None:
        self._trigger_canvas.destroy()
        self._record_touch(event)
        future = self._give_stimulus(self._attentation_stimulus)
        future.add_done_callback(self._start_stimulus_stage)

    def _start_stimulus_stage(self, _f: Future) -> None:
        self._give_stimulus(self._stimulus)
        self._backgroud.after(
            0, lambda: (self._create_target(), self._bind_second_stage())
        )

    def _on_second_touched(self, event: Event) -> None:
        self._trigger_canvas.destroy()
        self._record_touch(event)

        if self._is_go_trial:
            self._on_correct()
        else:
            self._on_incorrect()

    def _record_touch(self, event: Event) -> None:
        self._data.touch_events.append(
            TouchEvent(time=datetime.now().timestamp(), x=event.x, y=event.y)
        )

    # endregion

    # region result handlers
    def _on_correct(self) -> None:
        self._theater.aplayer.stop()
        self._trigger_canvas.destroy()

        self._backgroud.after(self._trial_config.reward_delay, self._give_reward)
        self._data.result = Result.CORRECT
        self._data.correct_rate = (self._animal_state.correct_trial + 1) / (
            self._animal_state.current_level_trial_id + 1
        )
        self._on_inter_trial()

    def _on_incorrect(self) -> None:
        self._theater.aplayer.stop()
        self._trigger_canvas.destroy()

        self._data.result = Result.INCORRECT
        self._data.correct_rate = self._animal_state.correct_trial / (
            self._animal_state.current_level_trial_id + 1
        )

        self._create_wrong_view()
        self._on_inter_trial()

    def _on_timeout(self) -> None:
        self._data.result = Result.TIMEOUT
        self._data.correct_rate = self._animal_state.correct_trial / (
            self._animal_state.current_level_trial_id + 1
        )
        self._create_wrong_view()
        self._on_inter_trial()

    # endregion

    # region stimulus and reward
    def _prepare_stimulus(
        self,
        freq1: int,
        dur1: int,
        freq2: int,
        dur2: int,
        total_duration: int,
    ) -> "NDArray[int16]":
        cycle = dur1 + dur2
        repeat = max(ceil(total_duration / cycle), 1)

        tone1 = ToneConfig(frequency=freq1, duration=dur1)
        tone2 = ToneConfig(frequency=freq2, duration=dur2)

        return self._theater.aplayer.generate_tone([tone1, tone2], repeat)

    def _give_stimulus(self, stimulus: "NDArray[int16]") -> "Future[bool]":
        return self._theater.aplayer.play(stimulus)

    def _give_reward(self) -> None:
        self._theater.reward.give_reward(self._trial_config.reward_duration)

    # endregion

    # region data
    def _init_data(self) -> None:
        self._data = TrialData(
            animal=self._animal_state.name,
            trial_id=self._animal_state.trial_id,
            current_level_trial_id=self._animal_state.current_level_trial_id,
            trial_config=self._trial_config,
            trial_start_time=datetime.now().timestamp(),
            trial_end_time=0,
            result=Result.TIMEOUT,
            correct_rate=0,
            touch_events=[],
        )

    # endregion
