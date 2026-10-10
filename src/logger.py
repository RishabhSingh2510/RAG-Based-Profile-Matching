import datetime
from pathlib import Path


class SessionLogger:
    """Handles timestamped real-time session logging into `./logs/` directory."""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize session logger and create a timestamped log file.

        Args:
            log_dir (str): Directory path to store log files. Defaults to 'logs'.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filepath = self.log_dir / f"session_{timestamp}.log"
        self.log("SESSION START", f"New session started. Log file: '{self.log_filepath}'")

    def log(self, category: str, message: str):
        """
        Append a timestamped log entry to the active log file.

        Args:
            category (str): Log entry label (e.g. 'USER QUERY', 'TOOL EXECUTION').
            message (str): Details string to log.
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(f"[{now_str}] [{category}] {message}\n")
