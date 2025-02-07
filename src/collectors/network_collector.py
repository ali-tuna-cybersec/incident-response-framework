import subprocess
import json
import logging
from pathlib import Path
import socket
import struct
from datetime import datetime
import os

class NetworkCollector:
    def __init__(self, case_id, config):
        self.case_id = case_id
        self.config = config
        self.evidence_path = Path(config['collection']['network']['evidence_path'])
        self.evidence_path.mkdir(parents=True, exist_ok=True)

    def collect(self):
        """Collect network-related evidence"""
        evidence = {
            "metadata": self._get_metadata(),
            "active_connections": self._get_active_connections(),
            "listening_ports": self._get_listening_ports(),
            "arp_cache": self._get_arp_cache(),
            "dns_cache": self._get_dns_cache(),
            "routing_table": self._get_routing_table()
        }
        
        # Save evidence to file
        output_file = self.evidence_path / f"{self.case_id}_network_evidence.json"
        with open(output_file, 'w') as f:
            json.dump(evidence, f, default=str)
        
        return evidence

    def _get_metadata(self):
        return {
            "collection_time": datetime.now().isoformat(),
            "collector": "NetworkCollector",
            "case_id": self.case_id
        }

    def _get_active_connections(self):
        connections = []
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output(['netstat', '-nao']).decode()
            else:  # Linux/Unix
                output = subprocess.check_output(['netstat', '-nutlp']).decode()
            
            for line in output.split('\n')[4:]:  # Skip header lines
                if line.strip():
                    connections.append(line.strip())
        except Exception as e:
            logging.error(f"Error collecting active connections: {e}")
        
        return connections

    def _get_listening_ports(self):
        ports = []
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output(['netstat', '-an', '|', 'findstr', 'LISTENING']).decode()
            else:  # Linux/Unix
                output = subprocess.check_output(['ss', '-lntu']).decode()
            
            for line in output.split('\n'):
                if line.strip():
                    ports.append(line.strip())
        except Exception as e:
            logging.error(f"Error collecting listening ports: {e}")
        
        return ports

    def _get_arp_cache(self):
        arp_entries = []
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output(['arp', '-a']).decode()
            else:  # Linux/Unix
                output = subprocess.check_output(['ip', 'neigh']).decode()
            
            for line in output.split('\n'):
                if line.strip():
                    arp_entries.append(line.strip())
        except Exception as e:
            logging.error(f"Error collecting ARP cache: {e}")
        
        return arp_entries

    def _get_dns_cache(self):
        dns_entries = []
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output(['ipconfig', '/displaydns']).decode()
            else:  # Linux/Unix
                # On Linux, you might need to use nscd or check /etc/hosts
                with open('/etc/hosts', 'r') as f:
                    output = f.read()
            
            for line in output.split('\n'):
                if line.strip():
                    dns_entries.append(line.strip())
        except Exception as e:
            logging.error(f"Error collecting DNS cache: {e}")
        
        return dns_entries

    def _get_routing_table(self):
        routes = []
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output(['route', 'print']).decode()
            else:  # Linux/Unix
                output = subprocess.check_output(['ip', 'route']).decode()
            
            for line in output.split('\n'):
                if line.strip():
                    routes.append(line.strip())
        except Exception as e:
            logging.error(f"Error collecting routing table: {e}")
        
        return routes

class LinuxCollector:
    def __init__(self, case_id, config, evidence_path):
        self.case_id = case_id
        self.config = config
        self.evidence_path = evidence_path

    def collect(self):
        # Implement the evidence collection logic here
        pass
