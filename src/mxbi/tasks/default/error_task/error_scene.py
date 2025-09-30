from tkinter import Canvas
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mxbi.models.animal import AnimalState
    from mxbi.models.session import SessionState
    from mxbi.theater import Theater


class ErrorScene:
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

    def __on_trial_end(self) -> None:
        self.__background.destroy()
        self.__theater.root.quit()

    def __create_objects(self) -> None:
        self.__background = Canvas(
            self.__theater.root,
            bg="red",
            width=self.__screen_type.width,
            height=self.__screen_type.height,
            highlightthickness=0,
        )
        self.__background.place(relx=0.5, rely=0.5, anchor="center")

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
