from tkinter import Canvas
from tkinter.ttk import Label
from typing import TYPE_CHECKING

from PIL import Image, ImageTk

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.theater import Theater
    from mxbi.models.animal import ScheduleCondition
    from mxbi.models.task import Feedback


class IDLEScene:
    def __init__(
        self,
        theater: "Theater",
        session_state: "SessionState",
        animal_state: "AnimalState",
    ) -> None:
        self._theater = theater
        self._session_config = session_state
        self._screen_type = self._session_config.session_config.screen_type

        self._on_trial_start()

    def start(self) -> "Feedback":
        self._theater.root.mainloop()

        return True

    def _on_trial_start(self) -> None:
        self._create_view()
        self._bind_events()

    def _on_trial_end(self) -> None:
        self._background.destroy()
        self._theater.root.quit()

    def _create_view(self) -> None:
        self._background = Canvas(
            self._theater.root,
            bg="black",
            width=self._screen_type.width,
            height=self._screen_type.height,
            highlightthickness=0,
        )
        self._background.place(relx=0.5, rely=0.5, anchor="center")

        xshift = 240
        xcenter = self._screen_type.width / 2 + xshift
        ycenter = self._screen_type.height / 2

        self._img = Image.open(
            "/Users/ccccr/repo/project/mxbi/mxbi-tasks/src/mxbi/tasks/default/idle_task/assets/apple_v1.png"
        )
        self._img = self._img.resize((400, 400)).rotate(-90, expand=True)
        self._img = ImageTk.PhotoImage(self._img)
        self.label_apple = Label(self._background, image=self._img)
        self.label_apple.place(x=xcenter, y=ycenter, anchor="center")

    def _bind_events(self) -> None:
        self._background.focus_set()
        self._background.bind("<r>", lambda e: self._give_reward(1000))

    def _give_reward(self, duration: int) -> None:
        self._theater.reward.give_reward(duration)

    def quit(self) -> None:
        self._background.destroy()
        self._theater.root.quit()

    def on_idle(self) -> None: ...

    def on_return(self) -> None: ...

    @property
    def condition(self) -> "ScheduleCondition | None":
        return None
