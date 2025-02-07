from jinja2 import Environment, FileSystemLoader
import os
import logging

class HTMLReporter:
    def __init__(self, config):
        self.config = config
        self.env = Environment(loader=FileSystemLoader(config['reporting']['template_path']))
        self.template = self.env.get_template('report_template.html')

    def generate_report(self, iocs, timeline, analysis_results, report_path):
        os.makedirs(report_path, exist_ok=True)
        output_file = os.path.join(report_path, 'report.html')
        
        with open(output_file, 'w') as f:
            html_content = self.template.render(iocs=iocs, timeline=timeline, analysis_results=analysis_results, company_name=self.config['reporting']['company_name'])
            f.write(html_content)
        
        logging.info(f"HTML report generated at {output_file}")