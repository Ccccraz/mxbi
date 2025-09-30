from concurrent.futures import Future
from datetime import datetime
from math import ceil
from random import randint
from tkinter import CENTER, Canvas, Event
from typing import TYPE_CHECKING, Final

from mxbi.models.session import ScreenConfig
from mxbi.tasks.GNGSiD.models import Result, TouchPoistion
from mxbi.tasks.GNGSiD.tasks.detect_double_touch.models import (
    TrialConfig,
    TrialData,
)
from mxbi.utils.aplayer import APlayer
from mxbi.utils.scene_utils import create_circle

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.theater import Theater


class GNGSiDDetectDoubleTouchScene:
    def __init__(
        self,
        theater: "Theater",
        animal_state: "AnimalState",
        screen_type: "ScreenConfig",
        trial_config: "TrialConfig",
    ) -> None:
        self._theater: "Final[Theater]" = theater
        self._animal_state: "Final[AnimalState]" = animal_state
        self._screen_type: "Final[ScreenConfig]" = screen_type
        self._trial_config = trial_config

        self._stimulus_duration_total: int = randint(
            self._trial_config.min_stimulus_duration,
            self._trial_config.max_stimulus_duration,
        )

        self._aplayer = APlayer()

        self._on_trial_start()

    # region public api
    def start(self) -> "TrialData":
        self._theater.mainloop()

        return self._data

    def cancle(self) -> None:
        self._data.result = Result.CANCEL
        self._on_trial_end()

    # endregion

    # region Lifecycle
    def _on_trial_start(self) -> None:
        self._create_view()
        self._bind_first_stage_events()
        self._init_data()

    def _on_inter_trial(self) -> None:
        self._backgroud.after(
            self._trial_config.inter_trial_interval, self._on_trial_end
        )

    def _on_trial_end(self) -> None:
        self._backgroud.destroy()
        self._theater.root.quit()

    # endregion

    # region Views
    def _create_view(self) -> None:
        self._backgroud = Canvas(
            self._theater.root,
            bg="black",
            width=self._screen_type.width,
            height=self._screen_type.height,
            highlightthickness=0,
        )
        self._backgroud.place(relx=0.5, rely=0.5, anchor="center")

        self._trigger_canvas = Canvas(
            self._backgroud,
            width=self._trial_config.stimulation_size,
            height=self._trial_config.stimulation_size,
            bg="lightgray",
            highlightthickness=0,
        )

        # TODO: figure out magic number
        xshift = 240
        xcenter = self._screen_type.width * 0.5 + xshift
        ycenter = self._screen_type.height * 0.5

        # TODO: figure out migic number
        circle_config = [(2.1, "#616161"), (3.1, "#bababa"), (6.3, "white")]
        for i in circle_config:
            create_circle(
                self._trial_config.stimulation_size / 2,
                self._trial_config.stimulation_size / 2,
                self._trial_config.stimulation_size / i[0],
                self._trigger_canvas,
                i[1],
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
    def _bind_first_stage_events(self) -> None:
        # Manual reward
        self._backgroud.focus_set()
        self._backgroud.bind("<r>", self._give_reward)

        # Trigger event
        self._trigger_canvas.bind("<ButtonPress>", self._on_touched)

        # Timeout event
        self._trigger_canvas.after(self._trial_config.time_out, self._on_timeout)

    def _bind_second_stage_events(self) -> None:
        self._trigger_canvas.bind("<ButtonPress>", self._on_correct)
        self._trigger_canvas.after(self._stimulus_duration_total, self._on_timeout)

    # endregion

    # region event handlers
    def _on_touched(self, event: Event) -> None:
        self._trigger_canvas.destroy()

        self._backgroud.after(
            self._trial_config.visual_stimulus_delay,
            lambda: (self._create_view(), self._bind_second_stage_events()),
        )

        self._data.trial_touched_time = datetime.now().timestamp()
        self._data.touched_coordinate = TouchPoistion(x=event.x, y=event.y)

    def _on_correct(self, e) -> None:
        self._trigger_canvas.destroy()
        print("correct")

        future = self._give_stimulus()
        future.add_done_callback(self._on_stimulus_complete)

        self._backgroud.after(
            2000, self._create_view
        )

        self._data.result = Result.CORRECT
        self._data.correct_rate = self._animal_state.correct_trial + 1 / (
            self._animal_state.current_level_trial_id + 1
        )

    def _on_incorrect(self, event: Event) -> None:
        self._trigger_canvas.destroy()

        self._data.trial_touched_time = datetime.now().timestamp()
        self._data.result = Result.INCORRECT
        self._data.correct_rate = self._animal_state.correct_trial / (
            self._animal_state.current_level_trial_id + 1
        )
        self._data.touched_coordinate = TouchPoistion(x=event.x, y=event.y)

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

    # region sitmulus and reward
    def _give_stimulus(self) -> Future[bool]:
        cycle = (
            self._trial_config.stimulus_duration_single
            + self._trial_config.stimulus_interval
        )
        repeat = ceil(self._stimulus_duration_total / cycle)
        repeat = max(repeat, 1)

        return self._aplayer.play_tone_async(
            frequency=self._trial_config.stimulus_frequency,
            duration=self._trial_config.stimulus_duration_single / 1000,
            repeat=repeat,
            interval=self._trial_config.stimulus_interval / 1000,
        )

    def _on_stimulus_complete(self, future: Future[bool]) -> None:
        if future.result():
            self._backgroud.after(
                self._trial_config.reward_delay, lambda: (self._give_reward(), self._on_inter_trial())
            )

    def _give_reward(self, _=None) -> None:
        self._theater.reward.give_reward(self._trial_config.reward_duration)

    # endregion

    # region data
    def _init_data(self):
        self._data = TrialData(
            animal=self._animal_state.name,
            trial_id=self._animal_state.trial_id,
            current_level_trial_id=self._animal_state.current_level_trial_id,
            trial_config=self._trial_config,
            trial_start_time=datetime.now().timestamp(),
            trial_touched_time=0,
            trial_end_time=0,
            result=Result.TIMEOUT,
            correct_rate=0,
            touched_coordinate=TouchPoistion(x=0, y=0),
        )

    # endregion
