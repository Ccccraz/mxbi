import json
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from mxbi.path import DATA_DIR_PATH
from mxbi.utils.logger import logger

if TYPE_CHECKING:
    from mxbi.models.session import SessionState

_now = datetime.now()


# TODO: The relationship between monkey and session
class DataLogger:
    def __init__(
        self, session_config: "SessionState", monkey: str, filename: str
    ) -> None:
        self.__session_state = session_config
        self._monkey = monkey
        self._filename = filename
        self._session_id = self.__session_state.session_id

        self.data_file = self._create_data_file()

    def _create_data_file(self) -> Path:
        try:
            filepath = self._gen_data_file_name()
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.touch(exist_ok=True)

            return filepath

        except FileExistsError as e:
            logger.error(f"Data file already exists: {e}")
            sys.exit(1)

        except Exception as e:
            logger.error(f"Failed to create data file: {e}")
            sys.exit(1)

    def _gen_data_file_name(self) -> Path:
        date_path = Path(f"{_now.year}{_now.month:02d}{_now.day:02d}")
        session_path = Path(f"session_{self._session_id}")
        monkey_path = Path(f"{self._monkey}")

        return (
            DATA_DIR_PATH
            / date_path
            / session_path
            / monkey_path
            / f"{self._filename}.jsonl"
        )

    def save_jsonl(self, data: dict) -> None:
        try:
            json_line = json.dumps(data, ensure_ascii=False)

            with open(self.data_file, "a", encoding="utf-8") as f:
                f.write(json_line + "\n")

        except TypeError as e:
            logger.error(f"Data is not JSON serializable: {e}")
            raise
        except IOError as e:
            logger.error(f"Failed to write to file {self.data_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while writing data: {e}")
            raise


if __name__ == "__main__":
    data = {"key": "value"}
    from datetime import datetime

    from mxbi.config import session_config
    from mxbi.models.session import SessionState

    state = SessionState(
        session_id=0,
        session_config=session_config.value,
        start_time=datetime.now().timestamp(),
        end_time=datetime.now().timestamp(),
    )

    recorder = DataLogger(state, "mock", "mock")

    for i in range(10):
        recorder.save_jsonl(data)
