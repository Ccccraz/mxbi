from concurrent.futures import Future
from datetime import datetime
from random import choice, randint
from tkinter import CENTER, Canvas, Event
from typing import TYPE_CHECKING, Final
from math import ceil

from mxbi.models.session import ScreenConfig
from mxbi.tasks.GNGSiD.models import Result, TouchPoistion
from mxbi.tasks.GNGSiD.tasks.frequency_discrimination_single_touch.models import (
    TrialConfig,
    TrialData,
)
from mxbi.utils.aplayer import ToneConfig
from mxbi.utils.scene_utils import create_circle

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.theater import Theater

    from numpy.typing import NDArray
    from numpy import int16


class GNGSiDFrequencyDiscriminationSingleTouchScene:
    def __init__(
        self,
        theater: "Theater",
        animal_state: "AnimalState",
        screen_tupe: "ScreenConfig",
        trial_config: "TrialConfig",
    ) -> None:
        self._theater: "Final[Theater]" = theater
        self._animal_state: "Final[AnimalState]" = animal_state
        self._screen_type: "Final[ScreenConfig]" = screen_tupe
        self._trial_config = trial_config

        self._stimulus_duration_total: int = randint(
            self._trial_config.min_stimulus_duration,
            self._trial_config.max_stimulus_duration,
        )
        self._freq = choice(self._trial_config.freq_match)
        self._tone = self._prepare_stimulus()

        self._on_trial_start()

    # region public api
    def start(self) -> "TrialData":
        self._theater.mainloop()

        return self._data

    def cancle(self) -> None:
        self._data.result = Result.CANCEL
        self._on_trial_end()

    # endregion

    # region lifecycle
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

    # region views
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

        create_circle(
            self._trial_config.stimulation_size * 0.5,
            self._trial_config.stimulation_size * 0.5,
            self._trial_config.stimulation_size / 3.1,
            self._trigger_canvas,
            "#616161",
        )
        create_circle(
            self._trial_config.stimulation_size * 0.5,
            self._trial_config.stimulation_size * 0.5,
            self._trial_config.stimulation_size / 6.3,
            self._trigger_canvas,
            "white",
        )
        create_circle(
            self._trial_config.stimulation_size * 0.25,
            self._trial_config.stimulation_size * 0.25,
            self._trial_config.stimulation_size / 6.3,
            self._trigger_canvas,
            "#616161",
        )
        create_circle(
            self._trial_config.stimulation_size * 0.75,
            self._trial_config.stimulation_size * 0.25,
            self._trial_config.stimulation_size / 6.3,
            self._trigger_canvas,
            "#616161",
        )
        create_circle(
            self._trial_config.stimulation_size * 0.25,
            self._trial_config.stimulation_size * 0.75,
            self._trial_config.stimulation_size / 6.3,
            self._trigger_canvas,
            "#616161",
        )
        create_circle(
            self._trial_config.stimulation_size * 0.75,
            self._trial_config.stimulation_size * 0.75,
            self._trial_config.stimulation_size / 6.3,
            self._trigger_canvas,
            "#616161",
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
        self._backgroud.bind("<r>", lambda e: self._give_reward())

        # Trigger event
        self._trigger_canvas.bind("<ButtonPress>", self._on_touched)

        # Timeout event
        self._trigger_canvas.after(self._trial_config.time_out, self._on_timeout)

    def _bind_second_stage_events(self) -> None:
        self._trigger_canvas.bind("<ButtonPress>", self._on_incorrect)

    # endregion

    # region event handlers
    def _on_touched(self, event: Event) -> None:
        self._trigger_canvas.destroy()
        self._give_stimulus(self._tone)

        self._backgroud.after(
            self._trial_config.sound_attention_duration,
            lambda: (self._create_view(), self._bind_second_stage_events()),
        )

        self._data.trial_touched_time = datetime.now().timestamp()
        self._data.touched_coordinate = TouchPoistion(x=event.x, y=event.y)

    def _on_correct(self) -> None:
        self._backgroud.after(self._trial_config.reward_delay, self._give_reward)

        self._trigger_canvas.destroy()

        self._data.result = Result.CORRECT
        self._data.correct_rate = self._animal_state.correct_trial + 1 / (
            self._animal_state.current_level_trial_id + 1
        )

        self._on_inter_trial()

    def _on_incorrect(self, event: Event) -> None:
        self._theater.aplayer.stop()
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
    def _prepare_stimulus(self) -> "NDArray[int16]":
        cycle = self._trial_config.stimulus_duration_single * 2
        repeat = ceil(self._stimulus_duration_total / cycle)

        repeat = max(repeat, 1)

        freq_1 = ToneConfig(
            frequency=self._freq[0],
            duration=self._trial_config.stimulus_duration_single,
        )

        freq_2 = ToneConfig(
            frequency=self._freq[1],
            duration=self._trial_config.stimulus_duration_single,
        )

        return self._theater.aplayer.generate_tone([freq_1, freq_2], repeat)

    def _give_stimulus(self, tone: "NDArray[int16]"):
        future = self._theater.aplayer.play(tone)
        future.add_done_callback(self._on_stimulus_complete)

    def _on_stimulus_complete(self, future: Future[bool]) -> None:
        if future.result():
            self._trigger_canvas.after(0, self._on_correct)

    def _give_reward(self) -> None:
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
