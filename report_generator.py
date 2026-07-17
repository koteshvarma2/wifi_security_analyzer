import pandas as pd
from fpdf import FPDF
import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, exports_dir, reports_dir):
        self.exports_dir = exports_dir
        self.reports_dir = reports_dir
        
    def export_csv(self, networks_data, filename=None):
        if not filename:
            filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame(networks_data)
        # Drop complex types or simplify them for CSV if needed
        filepath = os.path.join(self.exports_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath
        
    def export_json(self, networks_data, filename=None):
        if not filename:
            filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.exports_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(networks_data, f, indent=4)
        return filepath
        
    def generate_pdf(self, networks_data, security_counts, channel_rec, filename=None):
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, text="WiFi Security Analyzer - Scan Report", ln=True, align='C')
        pdf.ln(5)
        
        # Meta
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, text=f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, text=f"Total Networks Found: {len(networks_data)}", ln=True)
        pdf.ln(5)
        
        # Security Distribution
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, text="Security Distribution:", ln=True)
        pdf.set_font("Arial", size=12)
        for sec, count in security_counts.items():
            if count > 0:
                pdf.cell(0, 10, text=f"  - {sec}: {count} network(s)", ln=True)
        pdf.ln(5)
                
        # Recommendations
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, text="Recommendations:", ln=True)
        pdf.set_font("Arial", size=12)
        
        # Simple rule-based recommendations
        pdf.cell(0, 8, text="- Avoid open networks for sensitive activity.", ln=True)
        pdf.cell(0, 8, text="- Upgrade your home router to WPA3 if available.", ln=True)
        pdf.cell(0, 8, text="- Use strong router passwords and keep firmware updated.", ln=True)
        if isinstance(channel_rec, dict):
            if channel_rec.get('2.4GHz'):
                pdf.cell(0, 8, text=f"- Recommended least congested 2.4GHz channel: {channel_rec['2.4GHz']}", ln=True)
            if channel_rec.get('5GHz'):
                pdf.cell(0, 8, text=f"- Recommended least congested 5GHz channel: {channel_rec['5GHz']}", ln=True)
        else:
            if channel_rec:
                pdf.cell(0, 8, text=f"- Recommended least congested 2.4GHz channel: {channel_rec}", ln=True)
            
        pdf.ln(10)
        
        # Networks Table
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, text="All Discovered Networks:", ln=True)
        
        # Table Header
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(50, 8, text="SSID", border=1)
        pdf.cell(35, 8, text="BSSID", border=1)
        pdf.cell(20, 8, text="Dist(m)", border=1, align='C')
        pdf.cell(45, 8, text="Security", border=1, align='C')
        pdf.cell(30, 8, text="Band/Ch", border=1, align='C')
        pdf.ln()
        
        # Table Rows
        pdf.set_font("Arial", size=9)
        for net in networks_data:
            ssid = (net.get('ssid') or "<Hidden>")[:25]
            pdf.cell(50, 8, text=ssid, border=1)
            pdf.cell(35, 8, text=str(net.get('bssid', '')), border=1)
            dist = f"{net.get('distance', 0):.2f}"
            pdf.cell(20, 8, text=dist, border=1, align='C')
            
            sec = str(net.get('security', ''))[:22]
            pdf.cell(45, 8, text=sec, border=1, align='C')
            
            band_ch = f"{net.get('channel', '')} ({net.get('band', '').replace(' GHz', 'G')})"
            pdf.cell(30, 8, text=band_ch, border=1, align='C')
            pdf.ln()
            
        pdf.output(filepath)
        return filepath
