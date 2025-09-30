from enum import StrEnum, auto

from mxbi.utils.detect_platform import Platform, detect_current_platform
from mxbi.utils.rewarder.mock_rewarder import MockReward
from mxbi.utils.rewarder.rewarder_protocol import RewarderProtocol


class PumpTable(StrEnum):
    MOCK = auto()
    RASBERRY = auto()


if detect_current_platform() == Platform.RASPBERRY:
    from mxbi.utils.rewarder.rasberrypi_gpio_rewarder import RasberryPiGPIORewarder

    reward_table: dict[PumpTable, type[RewarderProtocol]] = {
        PumpTable.MOCK: MockReward,
        PumpTable.RASBERRY: RasberryPiGPIORewarder,
    }
else:
    reward_table: dict[PumpTable, type[RewarderProtocol]] = {
        PumpTable.MOCK: MockReward,
    }


class Rewarder:
    def __init__(self, rewarder_type: PumpTable) -> None:
        self._rewarder: RewarderProtocol = self._init_pump(rewarder_type)

    def _init_pump(self, rewarder_type: PumpTable) -> RewarderProtocol:
        return reward_table[rewarder_type]()

    def give_reward(self, duration: int) -> None:
        self._rewarder.give_reward(duration)

    def stop_reward(self, all: bool) -> None:
        self._rewarder.stop_reward(all)

    def reverse(self) -> None:
        self._rewarder.reverse()
