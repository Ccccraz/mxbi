from threading import Thread
from typing import Callable

from mxbi.animal_detector.animal_detector import AnimalDetector, DetectionResult
from mxbi.peripheral.rfid.dorset_lid665v42 import DorsetLID665v42
from mxbi.peripheral.rfid.dorset_lid665v42 import Result


class DorsetLID665v42Detector(AnimalDetector):
    def __init__(self, theater, port: str, baudrate: int) -> None:
        super().__init__(theater)
        self._scanner = DorsetLID665v42(port, baudrate)

        self._reader_thread: Thread | None = None
        self._callback: Callable[[Result], None] | None = None

    def _start_detection(self) -> None:
        self._scanner.open()

        self._callback = self._handle_result
        self._scanner.subscribe(self._callback)

        self._reader_thread = Thread(
            target=self._scanner.read,
            name="DorsetLID665v42Reader",
            daemon=True,
        )
        self._reader_thread.start()

    def _stop_detection(self) -> None:
        if self._callback is not None:
            self._scanner.unsubscribe(self._callback)
            self._callback = None

        self._scanner.close()
        if self._reader_thread is not None:
            self._reader_thread.join(timeout=1.0)
            self._reader_thread = None

    def _handle_result(self, result: Result) -> None:
        detect_result = DetectionResult(result.animal_id, False)
        self.process_detection(detect_result)
