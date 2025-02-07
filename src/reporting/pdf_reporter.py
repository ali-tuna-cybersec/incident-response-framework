from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import logging

class PDFReporter:
    def __init__(self, config):
        self.config = config

    def generate_report(self, iocs, timeline, analysis_results, report_path):
        os.makedirs(report_path, exist_ok=True)
        output_file = os.path.join(report_path, 'report.pdf')
        
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        
        c.drawString(100, height - 100, f"Company: {self.config['reporting']['company_name']}")
        c.drawString(100, height - 120, "Indicators of Compromise:")
        y = height - 140
        for ioc_type, ioc_values in iocs.items():
            c.drawString(100, y, f"{ioc_type.capitalize()}:")
            y -= 20
            for ioc in ioc_values:
                c.drawString(120, y, str(ioc))
                y -= 20
        
        c.drawString(100, y - 20, "Timeline:")
        y -= 40
        for event in timeline:
            c.drawString(100, y, str(event))
            y -= 20
        
        c.drawString(100, y - 20, "Analysis Results:")
        y -= 40
        for result in analysis_results:
            c.drawString(100, y, str(result))
            y -= 20
        
        c.save()
        
        logging.info(f"PDF report generated at {output_file}")