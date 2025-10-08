from enum import StrEnum, auto

from mxbi.peripheral.pumps.mock_pump import MockPump
from mxbi.peripheral.pumps.rewarder import Rewarder


class PumpEnum(StrEnum):
    MOCK = auto()
    RASBERRY_PI_GPIO = auto()


DEFAULT_PUMP = PumpEnum.RASBERRY_PI_GPIO


class PumpFactory:
    """Factory responsible for creating rewarder instances."""

    pumps: dict[PumpEnum, type[Rewarder]] = {DEFAULT_PUMP: MockPump}

    @classmethod
    def create(cls, rewarder_type: PumpEnum) -> Rewarder:
        try:
            rewarder_cls = cls.pumps[rewarder_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported rewarder type: {rewarder_type}") from exc
        return rewarder_cls()
