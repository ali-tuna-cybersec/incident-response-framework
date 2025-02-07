import wmi
import psutil
import os
import json
import shutil
from datetime import datetime
import logging
from pathlib import Path

try:
    import win32evtlog
except ImportError:
    win32evtlog = None

class WindowsCollector:
    def __init__(self, config, log_file_path, evidence_path):
        self.config = config
        self.log_file_path = log_file_path
        self.evidence_path = Path(evidence_path)
        self.evidence_path.mkdir(parents=True, exist_ok=True)
        self.wmi = wmi.WMI()

    def collect(self):
        if win32evtlog is None:
            logging.error("win32evtlog module is not available. Ensure you are running on Windows.")
            return None

        evidence = {
            "metadata": self._get_metadata(),
            "processes": self._get_processes(),
            "network": self._get_network_connections(),
            "services": self._get_services(),
            "scheduled_tasks": self._get_scheduled_tasks(),
            "system_info": self._get_system_info(),
            "event_logs": self._get_event_logs()
        }
        
        self.collect_log_file()

        output_file = self.evidence_path / f"windows_evidence.json"
        with open(output_file, 'w') as f:
            json.dump(evidence, f, indent=4)
        
        return self.evidence_path

    def _get_metadata(self):
        return {
            "timestamp": datetime.now().isoformat()
        }

    def _get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(proc.info)
        return processes

    def _get_network_connections(self):
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            connections.append(conn._asdict())
        return connections

    def _get_services(self):
        services = []
        for service in self.wmi.Win32_Service():
            services.append({
                "name": service.Name,
                "state": service.State,
                "start_mode": service.StartMode,
                "start_name": service.StartName
            })
        return services

    def _get_scheduled_tasks(self):
        tasks = []
        for task in self.wmi.Win32_ScheduledJob():
            tasks.append({
                "job_id": task.JobId,
                "name": task.Name,
                "start_time": task.StartTime,
                "status": task.Status
            })
        return tasks

    def _get_system_info(self):
        system_info = {}
        for os_info in self.wmi.Win32_OperatingSystem():
            system_info = {
                "name": os_info.Name,
                "version": os_info.Version,
                "manufacturer": os_info.Manufacturer,
                "configuration": os_info.Configuration,
                "build_type": os_info.BuildType
            }
        return system_info

    def _get_event_logs(self):
        log_types = ["System", "Application", "Security"]
        event_logs = {}
        for log_type in log_types:
            log = win32evtlog.OpenEventLog(None, log_type)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(log, flags, 0)
            event_logs[log_type] = []
            for event in events:
                event_logs[log_type].append({
                    "event_category": event.EventCategory,
                    "time_generated": event.TimeGenerated.isoformat(),
                    "source_name": event.SourceName,
                    "event_id": event.EventID,
                    "event_type": event.EventType,
                    "event_data": event.StringInserts
                })
            win32evtlog.CloseEventLog(log)
        return event_logs

    def collect_log_file(self):
        if os.path.exists(self.log_file_path):
            shutil.copy(self.log_file_path, self.evidence_path / "log_file.txt")
        else:
            logging.warning(f"{self.log_file_path} does not exist")