from datetime import datetime
import logging
from pathlib import Path
import json
import os

class TimelineAnalyzer:
    def __init__(self, config):
        self.config = config
        self.max_events = config['analysis']['timeline_max_events']
        self.timeline = []

    def build_timeline(self, evidence_path):
        """Build a timeline of events from the evidence."""
        timeline = []
        log_file = os.path.join(evidence_path, "log_file.txt")
        
        if not os.path.exists(log_file):
            logging.warning(f"Log file {log_file} does not exist.")
            return timeline
        
        with open(log_file, 'r') as f:
            for line in f:
                # Placeholder for actual timeline building logic
                event = {
                    "timestamp": "2023-01-01T00:00:00Z",  # Placeholder timestamp
                    "event": line.strip()
                }
                timeline.append(event)
        
        logging.info(f"Built timeline with {len(timeline)} events from the log file.")
        return timeline

    def _process_evidence(self, data):
        # Process Windows evidence
        if 'event_logs' in data:
            for event in data['event_logs']:
                self._add_event(
                    timestamp=event['time_generated'],
                    source='Windows Event Log',
                    event_type=event['event_id'],
                    description=f"{event['source']} - {event['event_category']}"
                )

        # Process Linux evidence
        if 'auth_logs' in data:
            for log_entry in data['auth_logs']:
                if 'timestamp' in log_entry:  # Requires parsed timestamps
                    self._add_event(
                        timestamp=log_entry['timestamp'],
                        source='Linux Auth Log',
                        description=log_entry['message']
                    )

        # Process processes
        if 'processes' in data:
            for process in data['processes']:
                if 'create_time' in process:
                    self._add_event(
                        timestamp=process['create_time'],
                        source='Process',
                        description=f"Process started: {process['name']} (PID: {process['pid']})"
                    )

    def _add_event(self, timestamp, source, description, event_type=None):
        try:
            parsed_time = datetime.fromisoformat(timestamp)
            self.timeline.append({
                'timestamp': parsed_time,
                'source': source,
                'type': event_type,
                'description': description
            })
        except Exception as e:
            logging.error(f"Error parsing timestamp {timestamp}: {e}")
