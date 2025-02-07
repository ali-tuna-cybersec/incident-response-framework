import os
import shutil
import logging
from pathlib import Path

class LinuxCollector:
    def __init__(self, config, log_file_path, evidence_path):
        self.config = config
        self.log_file_path = log_file_path
        self.evidence_path = Path(evidence_path)
        
        if self.evidence_path.is_file():
            raise ValueError(f"Evidence path {self.evidence_path} is a file, not a directory.")
        
        self.evidence_path.mkdir(parents=True, exist_ok=True)

    def collect(self):
        logging.info(f"Collecting evidence from {self.log_file_path}")
        
        self.collect_log_file()

        return self.evidence_path

    def collect_log_file(self):
        if os.path.exists(self.log_file_path):
            shutil.copy(self.log_file_path, self.evidence_path / "log_file.txt")
        else:
            logging.warning(f"{self.log_file_path} does not exist")