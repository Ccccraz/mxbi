from mxbi.animal_detector.animal_detector import AnimalDetector, DetectionResult
from mxbi.utils.logger import logger


class DebugDetector(AnimalDetector):
    def __init__(self, theater) -> None:
        super().__init__(theater)

        self.__result = DetectionResult("mock_001", False)
        self._theater.root.bind("<p>", self.__on_mock_001_animal_entered)
        self._theater.root.bind("<o>", self.__on_mock_002_animal_entered)
        self._theater.root.bind("<l>", self.__on_mock_animal_left)
        self._theater.root.bind("<c>", self.__on_mock_animal_changed)
        self._theater.root.bind("<e>", self.__on_mock_error)

    def _detect_animal(self) -> DetectionResult:
        return self.__result

    def __on_mock_001_animal_entered(self, _) -> None:
        self.__result = DetectionResult("mock_001", False)
        logger.info("Mock_001 animal entered")

    def __on_mock_002_animal_entered(self, _) -> None:
        self.__result = DetectionResult("mock_002", False)
        logger.info("Mock_002 animal entered")

    def __on_mock_animal_left(self, _) -> None:
        self.__result = DetectionResult(None, False)
        logger.info("Mock animal left")

    def __on_mock_animal_changed(self, _) -> None:
        if self.__result.animal_name == "mock_001":
            self.__result = DetectionResult("mock_002", False)
            logger.info("Mock animal changed to mock_002")
        else:
            self.__result = DetectionResult("mock_001", False)
            logger.info("Mock animal changed to mock_001")

    def __on_mock_error(self, _) -> None:
        self.__result = DetectionResult(None, True)
        logger.info("detect error")
