from typing import TYPE_CHECKING

from mxbi.animal_detector.animal_detector import AnimalDetector, DetectorEvent
from mxbi.animal_detector.debug_detector import DebugDetector
from mxbi.config import session_config
from mxbi.models.animal import AnimalState
from mxbi.models.scheduler import SchedulerState, ScheduleRunningStateEnum
from mxbi.models.task import TaskEnum
from mxbi.tasks.task import Task
from mxbi.tasks.task_table import task_table
from mxbi.utils.logger import logger

if TYPE_CHECKING:
    from mxbi.theater import Theater
    from mxbi.models.task import Feedback


class Scheduler:
    def __init__(self, theater: "Theater") -> None:
        self._theater = theater
        self._detector: AnimalDetector = DebugDetector(theater)

        self._animal_states = {
            animal.name: AnimalState(
                name=animal.name, task=animal.task, level=animal.level
            )
            for animal in session_config.value.animals.values()
        }

        self._state = SchedulerState(
            running=False,
            state=ScheduleRunningStateEnum.SCHEDULE,
            animal_state=None,
        )
        self._state.current_task = None

        self._bind_events()

    def _bind_events(self) -> None:
        self._theater.register_event_quit(self.quit)

        self._detector.register_event(
            DetectorEvent.ANIMAL_ENTERED, self._on_animal_entered
        )
        self._detector.register_event(
            DetectorEvent.ANIMAL_RETUREND, self._on_animal_returned
        )
        self._detector.register_event(DetectorEvent.ANIMAL_LEFT, self._on_animal_left)
        self._detector.register_event(
            DetectorEvent.ANIMAL_CHANGED, self._on_animal_changed
        )
        self._detector.register_event(
            DetectorEvent.ERROR_DETECTED, self._on_detect_error
        )

    def _start(self) -> None:
        self._state.running = True
        while self._state.running:
            match self._state.state:
                case ScheduleRunningStateEnum.IDLE:
                    self._idle()
                case ScheduleRunningStateEnum.SCHEDULE:
                    self._schedule_tasks()
                case ScheduleRunningStateEnum.ERROR:
                    self._error("Error detected")

    def _schedule_tasks(self) -> None:
        if self._state.animal_state is None:
            self._state.state = ScheduleRunningStateEnum.IDLE
            return

        try:
            self._state.current_task = self._create_task(self._state.animal_state)
            feedback = self._state.current_task.start()

            self._handle_task_feedback(self._state.animal_state, feedback)
        except Exception as e:
            raise e

        finally:
            self._state.current_task = None

    def _create_task(self, monkey_state: "AnimalState") -> "Task":
        task_class = self._select_task(monkey_state.task)
        task = task_class(self._theater, self._theater._session_state, monkey_state)

        monkey_state.condition = task.condition

        return task

    def _handle_task_feedback(
        self, monkey: "AnimalState", feedback: "Feedback"
    ) -> None:
        if self._state.current_task is None:
            return

        monkey.update(feedback)
        self._evaluate_and_adjust_difficulty(monkey)

    def _idle(self) -> None:
        self._state.current_task = task_table[TaskEnum.IDEL](
            self._theater, self._theater._session_state, AnimalState()
        )
        self._state.current_task.start()

    def _error(self, error: str) -> None:
        self._state.current_task = task_table[TaskEnum.ERROR](
            self._theater, self._theater._session_state, AnimalState()
        )
        self._state.current_task.start()

    def quit(self) -> None:
        for i in self._animal_states.values():
            i.trial_id = 0
            i.reset()

        session_config.save()

        self._state.running = False
        self._detector.quit()
        if self._state.current_task is not None:
            self._state.current_task.quit()

    def start(self) -> None:
        self._detector.start()
        self._start()

    def _get_animal_state(self, monkey: str) -> AnimalState:
        return self._animal_states[monkey]

    def _select_task(self, task_enum: TaskEnum) -> type[Task]:
        return task_table[task_enum]

    def _evaluate_and_adjust_difficulty(self, state: "AnimalState") -> None:
        if state.condition is None:
            return

        if state.current_level_trial_id < state.condition.evaluation_interval:
            return

        if state.correct_rate >= state.condition.difficulty_increase_threshold:
            self._increase_difficulty(state)
        elif state.correct_rate <= state.condition.difficulty_decrease_threshold:
            self._decrease_difficulty(state)

    def _increase_difficulty(self, state: "AnimalState") -> None:
        if state.condition is None:
            return

        if state.level < state.condition.level_count:
            state.level += 1
            logger.debug(f"Increasing difficulty to level {state.level}")
        else:
            state.task = state.condition.next_task
        state.reset()
        session_config.save()

    def _decrease_difficulty(self, state: "AnimalState") -> None:
        if state.level > 0:
            state.level -= 1
            state.reset()
            session_config.save()

    def _on_animal_entered(self, monkey: str) -> None:
        self._state.animal_state = self._get_animal_state(monkey)
        self._state.state = ScheduleRunningStateEnum.SCHEDULE
        if self._state.current_task is not None:
            self._state.current_task.quit()

    def _on_animal_returned(self, _: str) -> None:
        self._state.state = ScheduleRunningStateEnum.SCHEDULE
        if self._state.current_task is not None:
            self._state.current_task.on_return()

    def _on_animal_left(self, _: str) -> None:
        self._state.state = ScheduleRunningStateEnum.IDLE
        if self._state.current_task is not None:
            try:
                self._state.current_task.on_idle()
            except Exception as e:
                logger.error(e)
                self._state.current_task.quit()

    def _on_animal_changed(self, monkey: str) -> None:
        self._state.animal_state = self._get_animal_state(monkey)
        self._state.state = ScheduleRunningStateEnum.SCHEDULE
        if self._state.current_task is not None:
            self._state.current_task.quit()

    def _on_detect_error(self, _: str) -> None:
        self._state.state = ScheduleRunningStateEnum.ERROR
        if self._state.current_task is not None:
            self._state.current_task.quit()


if __name__ == "__main__":
    # TODO: Add main function
    pass
