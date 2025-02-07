import argparse
import logging
import platform
import os
from pathlib import Path
import yaml

# Import collectors based on the operating system
system_platform = platform.system()
if system_platform == 'Windows':
    from collectors.windows_collector import WindowsCollector
else:
    from collectors.linux_collector import LinuxCollector

# Import analysis and reporting modules
from analysis.ioc_extractor import IOCExtractor
from analysis.timeline_analyzer import TimelineAnalyzer
from reporting.html_reporter import HTMLReporter
from reporting.pdf_reporter import PDFReporter

def load_config(config_path):
    """Load the configuration file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML config: {e}")
        raise
    except Exception as e:
        logging.error(f"Failed to load config from {config_path}: {e}")
        raise

def collect_evidence(config, log_file_path, evidence_path):
    """Collect evidence based on the operating system."""
    try:
        if system_platform == 'Windows':
            collector = WindowsCollector(config, log_file_path, evidence_path)
        else:
            collector = LinuxCollector(config, log_file_path, evidence_path)
        
        evidence = collector.collect()
        return evidence
    except Exception as e:
        logging.error(f"Failed to collect evidence: {e}")
        raise

def analyze_evidence(config, evidence_path):
    """Analyze the collected evidence."""
    try:
        ioc_extractor = IOCExtractor(config)
        iocs = ioc_extractor.extract_from_evidence(evidence_path)
        
        if not Path(evidence_path).exists():
            raise FileNotFoundError(f"Evidence path {evidence_path} does not exist.")
        
        timeline_analyzer = TimelineAnalyzer(config)
        timeline = timeline_analyzer.build_timeline(evidence_path)
        
        analysis_results = []  # Placeholder for additional analysis results
        return iocs, timeline, analysis_results
    except Exception as e:
        logging.error(f"Failed to analyze evidence: {e}")
        raise

def generate_reports(config, iocs, timeline, analysis_results, report_path):
    """Generate HTML and PDF reports."""
    try:
        html_reporter = HTMLReporter(config)
        html_reporter.generate_report(iocs, timeline, analysis_results, report_path)
        
        pdf_reporter = PDFReporter(config)
        pdf_reporter.generate_report(iocs, timeline, analysis_results, report_path)
    except Exception as e:
        logging.error(f"Failed to generate reports: {e}")
        raise

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Interactive prompts for user input
    log_file_path = input("Enter the path to the log file to be reported: ")
    evidence_path = input("Enter the path to save the collected evidence: ")
    report_path = input("Enter the path to save the generated reports: ")
    
    # Expand user and absolute paths
    log_file_path = os.path.abspath(os.path.expanduser(log_file_path))
    evidence_path = os.path.abspath(os.path.expanduser(evidence_path))
    report_path = os.path.abspath(os.path.expanduser(report_path))
    
    config = load_config("config/config.yaml")
    
    evidence = collect_evidence(config, log_file_path, evidence_path)
    
    iocs, timeline, analysis_results = analyze_evidence(config, evidence)
    
    generate_reports(config, iocs, timeline, analysis_results, report_path)

if __name__ == "__main__":
    main()