import re
import json
from pathlib import Path
import logging
import hashlib
import os

class IOCExtractor:
    def __init__(self, config):
        self.config = config
        self.ioc_types = config['analysis']['ioc_types']
        self.ioc_patterns = {
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'domain': r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b',
            'hash': r'\b[a-fA-F0-9]{32,128}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
        self.found_iocs = {ioc: set() for ioc in self.ioc_types}

    def extract_from_evidence(self, evidence_path):
        """Extract Indicators of Compromise (IOCs) from the evidence."""
        log_file = os.path.join(evidence_path, "log_file.txt")
        
        if not os.path.exists(log_file):
            logging.warning(f"Log file {log_file} does not exist.")
            return self.found_iocs
        
        with open(log_file, 'r') as f:
            for line in f:
                for ioc_type, pattern in self.ioc_patterns.items():
                    matches = re.findall(pattern, line)
                    self.found_iocs[ioc_type].update(matches)
        
        logging.info(f"Extracted IOCs: {self.found_iocs}")
        return self.found_iocs

    def _scan_data(self, data):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    self._scan_data(v)
                else:
                    self._check_iocs(str(v))
        elif isinstance(data, list):
            for item in data:
                self._scan_data(item)

    def _check_iocs(self, text):
        for ioc_type in self.ioc_types:
            pattern = self.ioc_patterns.get(ioc_type)
            if pattern:
                matches = re.findall(pattern, text)
                for match in matches:
                    if ioc_type == 'hash' and not self._is_valid_hash(match):
                        continue
                    self.found_iocs[ioc_type].add(match.lower())

    def _is_valid_hash(self, value):
        length = len(value)
        return length in (32, 40, 64)  # MD5, SHA-1, SHA-256
