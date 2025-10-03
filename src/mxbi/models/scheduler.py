from enum import Enum, auto

from pydantic import BaseModel, ConfigDict, PrivateAttr

from mxbi.models.animal import AnimalState
from mxbi.models.task import TaskEnum
from mxbi.tasks.task_protocol import Task


class ScheduleRunningStateEnum(Enum):
    IDLE = auto()
    SCHEDULE = auto()
    ERROR = auto()


class SchedulerConfig(BaseModel):
    task: TaskEnum = TaskEnum.IDEL
    level: int = 0


class SchedulerState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _current_task: Task | None = PrivateAttr(default=None)
    running: bool = False
    state: ScheduleRunningStateEnum = ScheduleRunningStateEnum.IDLE
    animal_state: AnimalState | None = None

    @property
    def current_task(self) -> Task | None:
        return self._current_task

    @current_task.setter
    def current_task(self, task: Task | None) -> None:
        self._current_task = task
