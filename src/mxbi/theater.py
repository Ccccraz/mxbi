from datetime import datetime
from tkinter import Event, Tk
from typing import Callable

from mxbi.config import session_config
from mxbi.data_logger import DataLogger
from mxbi.models.session import SessionConfig, SessionState
from mxbi.peripheral.pumps.pump_factory import PumpFactory
from mxbi.peripheral.pumps.rewarder import Rewarder
from mxbi.scheduler import Scheduler
from mxbi.utils.aplayer import APlayer


class Theater:
    def __init__(self) -> None:
        self._config = session_config.value
        self._session_state = SessionState(
            session_id=DataLogger.init_session_id(),
            start_time=datetime.now().timestamp(),
            session_config=self._config,
        )

        self._session_logger = DataLogger(self._session_state, "", "session_data")

        # callback for quit event
        self._on_quit: list[Callable[[], None]] = []

        self._rewarder = self._init_rewarder()
        self._aplayer = APlayer()

        # init theater
        self._init_tk()
        self._bind_event()

        self._scheduler = Scheduler(self)
        self._scheduler.start()

    def _init_rewarder(self) -> Rewarder:
        return PumpFactory.create(self._config.pump_type)

    def _init_tk(self) -> None:
        screen_type = session_config.value.screen_type
        self._root = Tk()

        self._root.title("mxbi")
        self._root.geometry(f"{screen_type.width}x{screen_type.height}")

        self._root.after(1000, lambda: self._root.attributes("-fullscreen", False))

    def _bind_event(self) -> None:
        self._root.bind("<Escape>", self._quit)

    def _quit(self, _: Event) -> None:
        self._session_state.end_time = datetime.now().timestamp()
        self._session_logger.save_json(self._session_state.model_dump())
        for callback in self._on_quit:
            callback()
        self._root.destroy()

    def register_event_quit(self, callback: Callable[[], None]) -> None:
        self._on_quit.append(callback)

    @property
    def reward(self) -> Rewarder:
        return self._rewarder

    @property
    def aplayer(self) -> APlayer:
        return self._aplayer

    def mainloop(self):
        self._root.mainloop()

    @property
    def root(self) -> Tk:
        return self._root

    @property
    def session_config(self) -> SessionConfig:
        return self._config


if __name__ == "__main__":
    theater = Theater()
    theater.root.mainloop()
