import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from config import APP_TITLE, APP_GEOMETRY, DEFAULT_THEME

class WiFiApp(ctk.CTk):
    def __init__(self, scanner, analyzer_module, database, report_gen, chart_module):
        super().__init__()
        self.scanner = scanner
        self.analyzer_module = analyzer_module
        self.database = database
        self.report_gen = report_gen
        self.chart_module = chart_module
        
        self.current_theme = self.database.get_setting("theme", DEFAULT_THEME)
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")
        
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        
        self.networks_data = []
        self.security_counts = {}
        self.channel_rec = None
        
        self.is_scanning = False
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="WiFi Analyzer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.scan_btn = ctk.CTkButton(self.sidebar, text="Scan Networks", command=self.start_scan)
        self.scan_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.export_pdf_btn = ctk.CTkButton(self.sidebar, text="Export PDF", command=self.export_pdf)
        self.export_pdf_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.export_csv_btn = ctk.CTkButton(self.sidebar, text="Export CSV", command=self.export_csv)
        self.export_csv_btn.grid(row=3, column=0, padx=20, pady=10)
        
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        self.auto_refresh_switch = ctk.CTkSwitch(self.sidebar, text="Auto Refresh", variable=self.auto_refresh_var, command=self.toggle_auto_refresh)
        self.auto_refresh_switch.grid(row=4, column=0, padx=20, pady=10)
        
        self.auto_refresh_id = None
        
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=7, column=0, padx=20, pady=20)
        if self.current_theme == "dark":
            self.theme_switch.select()
            
        discl = ctk.CTkLabel(self.sidebar, text="* 500m distance requires\nHigh-Gain antenna.", font=ctk.CTkFont(size=10), text_color="gray")
        discl.grid(row=8, column=0, padx=10, pady=5)
            
        # --- Main Content ---
        self.main_content = ctk.CTkFrame(self, corner_radius=10)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure((0, 1), weight=1)
        
        # Top bar (Search/Filter/Status)
        self.top_bar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.top_bar, text="Status: Ready", text_color="green")
        self.status_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.top_bar, mode="indeterminate")
        self.progress_bar.pack(side="left", padx=10, fill="x", expand=True)
        self.progress_bar.set(0)
        
        # Charts Area (Row 1)
        self.charts_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.charts_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.charts_frame.grid_columnconfigure((0, 1), weight=1)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        
        self.pie_chart_canvas = None
        self.bar_chart_canvas = None
        
        # Table Area (Row 2)
        self.table_frame = ctk.CTkFrame(self.main_content)
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.main_content.grid_rowconfigure(2, weight=1)
        
        self.setup_table()

    def setup_table(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure colors based on theme
        bg_color = "#333333" if self.current_theme == "dark" else "#ffffff"
        fg_color = "white" if self.current_theme == "dark" else "black"
        field_bg = "#2b2b2b" if self.current_theme == "dark" else "#f0f0f0"
        
        style.configure("Treeview", background=field_bg, foreground=fg_color, rowheight=25, fieldbackground=field_bg)
        style.map('Treeview', background=[('selected', '#1f538d')])
        
        columns = ("SSID", "BSSID", "Signal", "Dist(m)", "Band", "Channel", "Security")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        self.tree.bind("<Double-1>", self.show_network_details)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
            
        self.tree.column("SSID", width=180, anchor="w")
        self.tree.column("BSSID", width=130)
        
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
            
        self.database.set_setting("theme", self.current_theme)
        
        # Re-draw charts and table styles
        self.update_charts()
        self.setup_table()
        self.populate_table()
        
    def toggle_auto_refresh(self):
        if self.auto_refresh_var.get():
            self.schedule_auto_refresh()
        else:
            if self.auto_refresh_id:
                self.after_cancel(self.auto_refresh_id)
                self.auto_refresh_id = None

    def schedule_auto_refresh(self):
        from config import DEFAULT_REFRESH_INTERVAL
        self.auto_refresh_id = self.after(DEFAULT_REFRESH_INTERVAL * 1000, self.do_auto_refresh)
        
    def do_auto_refresh(self):
        if not self.is_scanning:
            self.start_scan()
        if self.auto_refresh_var.get():
            self.schedule_auto_refresh()
            
    def start_scan(self):
        if self.is_scanning:
            return
            
        status = self.scanner.check_status()
        if status == "No Adapter":
            messagebox.showerror("Error", "No WiFi adapter found.")
            return
            
        self.is_scanning = True
        self.scan_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Scanning...", text_color="orange")
        self.progress_bar.start()
        
        # Run scan in thread to avoid freezing GUI
        threading.Thread(target=self.run_scan_thread, daemon=True).start()
        
    def run_scan_thread(self):
        try:
            raw_results = self.scanner.scan()
            analyzed_networks, security_counts = self.analyzer_module.analyze_networks(raw_results)
            channel_recs, channels_dict = self.analyzer_module.get_channel_recommendation(analyzed_networks)
            
            # Update state
            self.networks_data = analyzed_networks
            self.security_counts = security_counts
            self.channel_rec = channel_recs
            self.channels_dict = channels_dict
            
            # Save to DB
            self.database.save_scan(self.networks_data, self.security_counts)
            
            # Update UI in main thread
            self.after(0, self.update_ui_post_scan)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda e=e: messagebox.showerror("Scan Error", str(e)))
            self.after(0, self.reset_scan_state)
            
    def update_ui_post_scan(self):
        self.populate_table()
        self.update_charts()
        self.reset_scan_state()
        self.status_label.configure(text=f"Status: Found {len(self.networks_data)} networks", text_color="green")
        
    def reset_scan_state(self):
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_bar.set(0)
        
    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for net in self.networks_data:
            self.tree.insert("", "end", values=(
                net.get('ssid', ''),
                net.get('bssid', ''),
                f"{net.get('signal', 0)} dBm",
                f"{net.get('distance', 0):.2f}",
                net.get('band', ''),
                net.get('channel', 0),
                net.get('security', '')
            ))
            
    def update_charts(self):
        if not self.networks_data:
            return
            
        is_dark = self.current_theme == "dark"
        
        # Clear existing charts safely
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        plt.close('all')
            
        # Pie Chart
        fig_pie = self.chart_module.create_security_pie_chart(self.security_counts, is_dark_mode=is_dark)
        self.pie_chart_canvas = FigureCanvasTkAgg(fig_pie, master=self.charts_frame)
        self.pie_chart_canvas.draw()
        self.pie_chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10)
        
        # Bar Chart
        if hasattr(self, 'channels_dict'):
            fig_bar = self.chart_module.create_channel_bar_chart(self.channels_dict, is_dark_mode=is_dark)
            self.bar_chart_canvas = FigureCanvasTkAgg(fig_bar, master=self.charts_frame)
        self.bar_chart_canvas.draw()
        self.bar_chart_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=10)
        
    def export_pdf(self):
        if not self.networks_data:
            messagebox.showwarning("No Data", "Please run a scan first.")
            return
        try:
            filepath = self.report_gen.generate_pdf(self.networks_data, self.security_counts, self.channel_rec)
            messagebox.showinfo("Export Successful", f"PDF report saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            
    def export_csv(self):
        if not self.networks_data:
            messagebox.showwarning("No Data", "Please run a scan first.")
            return
        try:
            filepath = self.report_gen.export_csv(self.networks_data)
            messagebox.showinfo("Export Successful", f"CSV export saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            
    def show_network_details(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        values = item['values']
        bssid = values[1]
        
        net_data = next((n for n in self.networks_data if n['bssid'] == bssid), None)
        if not net_data: return
        
        # Simple MAC Vendor lookup
        oui = bssid[:8].upper()
        vendor = "Unknown Vendor"
        known_ouis = {
            "48:55:5E": "Jio (Reliance)", "72:22:F3": "Jio (Reliance)", "6A:22:F3": "Jio (Reliance)",
            "7A:E5:32": "Jio (Reliance)", "6A:BB:C1": "Jio (Reliance)", "72:E5:32": "Jio (Reliance)",
            "CA:BB:C1": "Jio (Reliance)", "B2:BB:C1": "Jio (Reliance)", "9A:78:C9": "Jio (Reliance)",
            "82:BB:C1": "Jio (Reliance)", "8A:BB:C1": "Jio (Reliance)", "72:6B:41": "Jio (Reliance)",
            "C4:EA:1D": "TP-Link", "B0:BE:76": "TP-Link",
            "A0:04:60": "Netgear", "08:BD:43": "Netgear",
            "E4:5F:01": "Cisco", "00:14:22": "Dell",
            "00:1A:11": "Google", "F4:F5:D8": "Google"
        }
        for k, v in known_ouis.items():
            if bssid.upper().startswith(k):
                vendor = v
                break
                
        popup = ctk.CTkToplevel(self)
        popup.title(f"Details - {net_data.get('ssid')}")
        popup.geometry("450x550")
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text=f"{net_data.get('ssid')} ({bssid})", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 5))
        
        scroll_frame = ctk.CTkScrollableFrame(popup)
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        import urllib.request
        import json
        lat, lon = "Unavailable", "Unavailable"
        city, district, state, pincode = "Unknown", "Unknown", "Unknown", "Unknown"
        mandal = "Unknown"
        try:
            req = urllib.request.urlopen("http://ip-api.com/json/?fields=status,lat,lon", timeout=1.5)
            data = json.loads(req.read().decode())
            if data.get("status") == "success":
                lat = data.get("lat")
                lon = data.get("lon")
                
                # Fetch detailed District/Mandal using OpenStreetMap Reverse Geocoding
                osm_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
                osm_req = urllib.request.Request(osm_url, headers={'User-Agent': 'WiFiSecurityAnalyzer/1.0'})
                osm_resp = urllib.request.urlopen(osm_req, timeout=2.0)
                osm_data = json.loads(osm_resp.read().decode())
                addr = osm_data.get("address", {})
                
                city = addr.get("city", addr.get("town", addr.get("village", "Unknown")))
                district = addr.get("state_district", addr.get("county", "Unknown"))
                mandal = addr.get("suburb", addr.get("neighbourhood", addr.get("municipality", "Unknown")))
                state = addr.get("state", "Unknown")
                pincode = addr.get("postcode", "Unknown")
        except Exception:
            pass
            
        sec_tier = net_data.get('security', 'Unknown')
        cipher = net_data.get('cipher', '')
        dist = net_data.get('distance', 0)
        band = net_data.get('band', '')
        signal = net_data.get('signal', -100)
        
        threats = []
        
        # 1. Encryption Core Status
        if "Open" in sec_tier or "None" in sec_tier:
            threats.append("❌ STATUS: NOT SECURE (CRITICAL RISK)")
            threats.append(f"• {net_data.get('ssid')} has NO encryption. Data is sent in plaintext and can be intercepted by anyone nearby.")
        elif "WEP" in sec_tier:
            threats.append("❌ STATUS: NOT SECURE (HIGH RISK)")
            threats.append(f"• {net_data.get('ssid')} uses WEP, a deprecated protocol that can be cracked in minutes.")
        elif "WPA2" in sec_tier and "TKIP" in cipher:
            threats.append("⚠️ STATUS: MODERATE RISK (WEAK CIPHER)")
            threats.append(f"• {net_data.get('ssid')} uses legacy TKIP. It is susceptible to cryptographic cracking.")
        elif "WPA3" in sec_tier:
            threats.append("✅ STATUS: HIGHLY SECURE")
            threats.append(f"• {net_data.get('ssid')} uses modern SAE, making it immune to offline dictionary brute-forcing.")
        else:
            threats.append("✅ STATUS: SECURE (INDUSTRY STANDARD)")
            threats.append(f"• {net_data.get('ssid')} uses robust AES. It is safe, but vulnerable to 4-way handshake capture if the password is weak.")
            
        # 2. Range & Physical Security
        if dist < 15:
            threats.append(f"• Close Proximity ({dist:.1f}m): Attackers can easily intercept handshakes from right outside the walls.")
        elif dist < 60:
            threats.append(f"• Moderate Range ({dist:.1f}m): Vulnerable to attackers scanning from adjacent buildings or vehicles.")
        else:
            threats.append(f"• Long Range ({dist:.1f}m): Remote physical eavesdropping would require highly specialized directional antennas.")
            
        # 3. Band Vulnerability
        if "5" in band:
            threats.append("• 5GHz Band: The shorter physical range of 5GHz waves makes remote Wardriving attacks more difficult.")
        else:
            threats.append("• 2.4GHz Band: The longer physical range increases the 'blast radius' for potential attackers to listen in.")
            
        # 4. Signal / Evil Twin Risk
        if signal < -75:
            threats.append("• Weak Signal Risk: The low signal causes frequent disconnections, making devices vulnerable to 'Evil Twin' rogue AP attacks.")
        else:
            threats.append("• Strong Signal: A high signal strength makes it harder for a hacker to overpower the network with a rogue access point.")
            
        sections = {
            "Basic Info": [
                f"Network Name (SSID): {net_data.get('ssid')}",
                f"MAC Address (BSSID): {bssid}",
                f"Hardware Vendor: {vendor}",
                f"Network Type: Infrastructure"
            ],
            "Signal & Range": [
                f"Frequency Band: {net_data.get('band')} ({net_data.get('radio')})",
                f"Operating Frequency: {net_data.get('freq')} MHz",
                f"Channel: {net_data.get('channel')}",
                f"Signal Strength (RSSI): {net_data.get('signal')} dBm",
                f"Estimated Distance: {net_data.get('distance', 0):.2f} meters"
            ],
            "Security Details": [
                f"Overall Tier: {net_data.get('security')}",
                f"Authentication: {net_data.get('auth')}",
                f"Cipher Suite: {net_data.get('cipher')}",
                f"Analyzer Score: {net_data.get('score')}/100"
            ],
            "Security Threats & Risks": threats,
            "Approx. Location (Scanner)": [
                f"Latitude: {lat}",
                f"Longitude: {lon}",
                f"City / Area: {city}",
                f"Mandal / Suburb: {mandal}",
                f"District: {district}",
                f"State / Region: {state}",
                f"Pincode: {pincode}"
            ]
        }
        
        for sec_name, sec_items in sections.items():
            ctk.CTkLabel(scroll_frame, text=sec_name, font=ctk.CTkFont(size=14, weight="bold"), text_color="#1f538d").pack(anchor="w", pady=(10, 2))
            for item in sec_items:
                ctk.CTkLabel(scroll_frame, text=item, anchor="w", justify="left").pack(fill="x", padx=10, pady=2)
                
        ctk.CTkLabel(popup, text="* Distance is a mathematical estimate via FSPL.\n* Location is based on Scanner IP Geolocation.", 
                     font=ctk.CTkFont(size=10, slant="italic"), text_color="gray").pack(pady=(0, 10))
