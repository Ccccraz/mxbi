import sys

from mxbi.utils.logger import logger

from queue import Empty, Queue
from threading import Event, Thread
from time import sleep

PUMP_PIN: int = 13

try:
    import RPi.GPIO as GPIO  # type: ignore
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.LOW)
except ImportError:
    logger.error("RPi.GPIO is not installed")
    sys.exit(1)



class RasberryPiGPIORewarder:
    def __init__(self) -> None:
        self._stop_event: Event = Event()
        self._working: bool = False
        self._worker_threading: Thread = Thread(target=self._worker)
        self._task_queue: Queue[int] = Queue()

        self._worker_threading.start()

    def _worker(self) -> None:
        self._workering = True
        while self._workering:
            try:
                duration = self._task_queue.get()
                self._stop_event.clear()
                self._give_reward(duration)

            except Empty:
                continue

    def _give_reward(self, duration: int) -> None:
        try:
            duration_sec = duration / 1000
            GPIO.output(PUMP_PIN, GPIO.HIGH)

            check_interval = 100
            elapsed = 0

            while elapsed < duration_sec and not self._stop_event.is_set():
                sleep_time = min(check_interval, duration_sec - elapsed)
                sleep(sleep_time)
                elapsed += sleep_time

            GPIO.output(PUMP_PIN, GPIO.LOW)

        except Exception as e:
            logger.warning(f"Error in _give_reward: {e}")
            try:
                GPIO.output(PUMP_PIN, GPIO.LOW)
            except Exception as e:
                logger.warning(f"Error in _give_reward: {e}")

    def give_reward(self, duration: int) -> None:
        self._task_queue.put(duration)

    def stop_reward(self, all: bool = False) -> None:
        if all:
            while not self._task_queue.empty():
                self._task_queue.get_nowait()

            self._stop_event.set()

        else:
            self._stop_event.set()
        GPIO.output(PUMP_PIN, GPIO.LOW)

    def __del__(self) -> None:
        self.stop_reward(True)
        self._workering = False
        self._worker_threading.join()

        GPIO.cleanup(PUMP_PIN)

    def reverse(self) -> None:
        raise NotImplementedError("Reverse operation is not supported by this device")
