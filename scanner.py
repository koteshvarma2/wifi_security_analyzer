import subprocess
import re
import platform
import logging

class WiFiScanner:
    def __init__(self):
        self.os_name = platform.system()
        
    def check_status(self):
        if self.os_name == "Windows":
            return "Enabled" # Assume enabled, netsh will fail otherwise
        return "Unknown OS"

    def scan(self, timeout=5):
        if self.os_name == "Windows":
            return self._scan_windows()
        else:
            raise Exception("Advanced scanning is currently only supported on Windows via netsh.")

    def _scan_windows(self):
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"], 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return self._parse_netsh(result.stdout)
        except Exception as e:
            logging.error(f"Error running netsh: {e}")
            return []
            
    def _parse_netsh(self, output):
        networks = []
        current_ssid = ""
        current_auth = ""
        current_cipher = ""
        
        # Regex patterns
        ssid_re = re.compile(r"^SSID\s+\d+\s+:\s+(.*)$")
        auth_re = re.compile(r"^\s+Authentication\s+:\s+(.*)$")
        cipher_re = re.compile(r"^\s+Encryption\s+:\s+(.*)$")
        bssid_re = re.compile(r"^\s+BSSID\s+\d+\s+:\s+([a-fA-F0-9:]+)$")
        signal_re = re.compile(r"^\s+Signal\s+:\s+(\d+)%$")
        band_re = re.compile(r"^\s+Band\s+:\s+(.*)$")
        channel_re = re.compile(r"^\s+Channel\s+:\s+(\d+)$")
        radio_re = re.compile(r"^\s+Radio type\s+:\s+(.*)$")
        
        current_bssid_block = {}
        
        for line in output.split('\n'):
            line = line.rstrip()
            if not line:
                continue
                
            m_ssid = ssid_re.match(line)
            if m_ssid:
                current_ssid = m_ssid.group(1).strip()
                continue
                
            m_auth = auth_re.match(line)
            if m_auth:
                current_auth = m_auth.group(1).strip()
                continue
                
            m_cipher = cipher_re.match(line)
            if m_cipher:
                current_cipher = m_cipher.group(1).strip()
                continue
                
            m_bssid = bssid_re.match(line)
            if m_bssid:
                if current_bssid_block:
                    networks.append(current_bssid_block)
                
                current_bssid_block = {
                    'ssid': current_ssid if current_ssid else "<Hidden Network>",
                    'auth': current_auth,
                    'cipher': current_cipher,
                    'bssid': m_bssid.group(1).strip(),
                    'freq': 2412, # Default fallback
                    'channel': 1,
                    'band': '2.4 GHz',
                    'radio': '802.11'
                }
                continue
                
            if current_bssid_block:
                m_sig = signal_re.match(line)
                if m_sig:
                    quality = int(m_sig.group(1))
                    dbm = (quality / 2) - 100
                    current_bssid_block['quality'] = quality
                    current_bssid_block['signal'] = dbm
                    continue
                    
                m_band = band_re.match(line)
                if m_band:
                    current_bssid_block['band'] = m_band.group(1).strip()
                    continue
                    
                m_chan = channel_re.match(line)
                if m_chan:
                    current_bssid_block['channel'] = int(m_chan.group(1))
                    # Assign approx frequency for distance math
                    if current_bssid_block.get('band') == '5 GHz':
                        current_bssid_block['freq'] = 5000 + (current_bssid_block['channel'] * 5)
                    else:
                        current_bssid_block['freq'] = 2412 + ((current_bssid_block['channel'] - 1) * 5)
                    continue
                    
                m_radio = radio_re.match(line)
                if m_radio:
                    current_bssid_block['radio'] = m_radio.group(1).strip()
                    continue
                    
        if current_bssid_block:
            networks.append(current_bssid_block)
            
        # Sort by signal strength
        networks.sort(key=lambda x: x.get('signal', -100), reverse=True)
        return networks
