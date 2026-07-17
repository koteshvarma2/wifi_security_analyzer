import sys
import os
sys.path.append(r"C:\Users\konakanchi kotesh\Downloads\wifi_security_analyzer")
from scanner import WiFiScanner
from analyzer import analyze_networks, get_channel_recommendation
from report_generator import ReportGenerator

def run():
    print("Initializing Scanner...")
    scanner = WiFiScanner()
    print("Status:", scanner.check_status())
    print("Scanning (this takes 3-5 seconds)...")
    
    raw = scanner.scan()
    analyzed, counts = analyze_networks(raw)
    recs, channels = get_channel_recommendation(analyzed)
    
    print("\n--- SCAN RESULTS ---")
    print(f"Total Networks Found: {len(analyzed)}")
    
    print("\nSecurity Distribution:")
    for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        if v > 0:
            print(f"  - {k}: {v}")
            
    print(f"\nRecommended Channels:")
    print(f"  - 2.4GHz: {recs.get('2.4GHz')}")
    print(f"  - 5GHz:   {recs.get('5GHz')}")
    
    print("\nAll Discovered Networks (Sorted by Signal Strength):")
    print(f"{'SSID':<25} | {'BSSID':<17} | {'Dist (m)':<8} | {'Security':<25} | {'Channel'}")
    print("-" * 90)
    for net in analyzed:
        ssid = net['ssid'][:24] if net['ssid'] else "<Hidden>"
        print(f"{ssid:<25} | {net['bssid']:<17} | {net['distance']:<8.2f} | {net['security']:<25} | {net['channel']} ({net['band']})")
        
    rg = ReportGenerator(
        r"C:\Users\konakanchi kotesh\Downloads\wifi_security_analyzer\exports",
        r"C:\Users\konakanchi kotesh\Downloads\wifi_security_analyzer\reports"
    )
    pdf_path = rg.generate_pdf(analyzed, counts, recs)
    print(f"\nReport generated at: {pdf_path}")

if __name__ == "__main__":
    run()
