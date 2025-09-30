from tkinter import Canvas
from tkinter.ttk import Label
from typing import TYPE_CHECKING

from PIL import Image, ImageTk

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.theater import Theater


class IDLEScene:
    def __init__(
        self,
        theater: "Theater",
        session_state: "SessionState",
        animal_state: "AnimalState",
    ) -> None:
        self.__theater = theater
        self.__session_config = session_state
        self.__screen_type = self.__session_config.session_config.screen_type

        self.__on_trial_start()

    def __on_trial_start(self) -> None:
        self.__create_objects()
        self.__bind_events()

    def __on_trial_end(self) -> None:
        self.__background.destroy()
        self.__theater.root.quit()

    def __create_objects(self) -> None:
        self.__background = Canvas(
            self.__theater.root,
            bg="black",
            width=self.__screen_type.width,
            height=self.__screen_type.height,
            highlightthickness=0,
        )
        self.__background.place(relx=0.5, rely=0.5, anchor="center")

        xshift = 240
        xcenter = self.__screen_type.width / 2 + xshift
        ycenter = self.__screen_type.height / 2

        self._img = Image.open(
            "/Users/ccccr/repo/project/mxbi/mxbi_refactor/mxbi/src/mxbi/tasks/idle_task/assets/apple_v1.png"
        )
        self._img = self._img.resize((400, 400)).rotate(-90, expand=True)
        self._img = ImageTk.PhotoImage(self._img)
        self.label_apple = Label(self.__background, image=self._img)
        self.label_apple.place(x=xcenter, y=ycenter, anchor="center")

    def __bind_events(self) -> None:
        self.__background.focus_set()
        self.__background.bind("<r>", lambda e: self.__on_reward(1000))

    def __on_reward(self, duration: int) -> None:
        self.__theater.reward.give_reward(duration)

    def __on_cancel(self) -> None:
        self.__on_trial_end()

    def start(self) -> None:
        self.__theater.mainloop()

    def quit(self) -> None:
        self.__on_cancel()

    def on_idle(self) -> None: ...

    def on_return(self) -> None:
        self.quit()

    @property
    def feedback(self) -> bool: ...

    @property
    def condition(self) -> None:
        return None
