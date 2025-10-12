from enum import StrEnum, auto
from typing import TYPE_CHECKING

from mxbi.detector.detector import Detector
from mxbi.detector.dorset_lid665v42_detector import DorsetLID665v42Detector
from mxbi.detector.mock_detector import MockDetector

if TYPE_CHECKING:
    from mxbi.theater import Theater


class DetectorEnum(StrEnum):
    MOCK = auto()
    DORSET_LID665V42 = auto()


class DetectorFactory:
    """Factory responsible for creating detector instances."""

    detectors: dict[DetectorEnum, type[Detector]] = {
        DetectorEnum.MOCK: MockDetector,
        DetectorEnum.DORSET_LID665V42: DorsetLID665v42Detector,
    }

    @classmethod
    def create(
        cls, detector_type: DetectorEnum, theater: "Theater", baudrate: int, port: str
    ) -> Detector:
        detector_cls = cls.detectors[detector_type]
        return detector_cls(theater, port, baudrate)
