from datetime import datetime
from tkinter import Event, Tk
from typing import Callable

from mxbi.config import session_config
from mxbi.data_logger import DataLogger
from mxbi.models.session import SessionConfig, SessionState
from mxbi.scheduler import Scheduler
from mxbi.utils.detect_platform import Platform
from mxbi.utils.rewarder.rewarder import PumpTable, Rewarder


class Theater:
    def __init__(self) -> None:
        self._config = session_config.value
        self._session_state = SessionState(
            session_id=0,
            start_time=datetime.now().timestamp(),
            session_config=self._config,
        )

        self._session_logger = DataLogger(self._session_state, "", "session_data")

        # callback for quit event
        self._on_quit: list[Callable[[], None]] = []

        self._rewarder = self._init_rewarder()

        # init theater
        self._init_tk()
        self._bind_event()

        self._scheduler = Scheduler(self)
        self._scheduler.start()

    def _init_rewarder(self) -> Rewarder:
        platform = self._config.platform

        pump_type: PumpTable = PumpTable.MOCK
        if (
            platform == Platform.WINDOWS
            or platform == Platform.LINUX
            or platform == Platform.MACOS
        ):
            pump_type = PumpTable.MOCK
        else:
            pump_type = PumpTable.RASBERRY

        return Rewarder(pump_type)

    def _init_tk(self) -> None:
        screen_type = session_config.value.screen_type
        self._root = Tk()

        self._root.title("mxbi")
        self._root.geometry(f"{screen_type.width}x{screen_type.height}")

        self._root.after(1000, lambda: self._root.attributes("-fullscreen", True))

    def _bind_event(self) -> None:
        self._root.bind("<Escape>", self._quit)

    def _quit(self, _: Event) -> None:
        self._session_state.end_time = datetime.now().timestamp()
        self._session_logger.save_jsonl(self._session_state.model_dump())
        for callback in self._on_quit:
            callback()
        self._root.destroy()

    def register_event_quit(self, callback: Callable[[], None]) -> None:
        self._on_quit.append(callback)

    @property
    def reward(self) -> Rewarder:
        return self._rewarder

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
