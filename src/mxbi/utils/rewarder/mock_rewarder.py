from mxbi.utils.logger import logger


class MockReward:
    def __init__(self) -> None:
        pass

    def give_reward(self, duration: int) -> None:
        logger.info(f"Mock reward given for {duration} seconds")

    def stop_reward(self, all: bool) -> None: ...

    def reverse(self) -> None: ...
