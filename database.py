import sqlite3
import os
import json
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Networks Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS networks (
                    bssid TEXT PRIMARY KEY,
                    ssid TEXT,
                    security_type TEXT,
                    last_seen DATETIME
                )
            ''')
            
            # Scan History Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_time DATETIME,
                    total_networks INTEGER,
                    networks_data TEXT,
                    security_distribution TEXT
                )
            ''')
            
            # User Settings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            conn.commit()

    def save_scan(self, networks, security_distribution):
        scan_time = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update individual networks
            for net in networks:
                cursor.execute('''
                    INSERT INTO networks (bssid, ssid, security_type, last_seen)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(bssid) DO UPDATE SET
                    ssid=excluded.ssid,
                    security_type=excluded.security_type,
                    last_seen=excluded.last_seen
                ''', (net['bssid'], net['ssid'], net['security'], scan_time))
            
            # Save scan event
            cursor.execute('''
                INSERT INTO scan_history (scan_time, total_networks, networks_data, security_distribution)
                VALUES (?, ?, ?, ?)
            ''', (
                scan_time,
                len(networks),
                json.dumps(networks),
                json.dumps(security_distribution)
            ))
            
            conn.commit()

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM user_settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return default
            
    def set_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            ''', (key, str(value)))
            conn.commit()

    def get_all_scans(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scan_history ORDER BY scan_time DESC')
            return [dict(row) for row in cursor.fetchall()]
