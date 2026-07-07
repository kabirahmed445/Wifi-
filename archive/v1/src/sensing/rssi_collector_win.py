import subprocess
import re
import time
from dataclasses import dataclass
from typing import List, Optional
import threading
from collections import deque

@dataclass
class WifiSample:
    rssi_dbm: float
    link_quality: float
    timestamp: float
    frequency_mhz: int = 0
    channel: int = 0

class WindowsWifiCollector:
    def __init__(self, interface="Wi-Fi", sample_rate_hz=2.0):
        self.interface = interface
        self.sample_rate_hz = sample_rate_hz
        self.samples: List[WifiSample] = []
        self.running = False
        self.thread = None
        
    def collect_once(self) -> WifiSample:
        """একটি RSSI স্যাম্পল সংগ্রহ করুন"""
        try:
            # netsh কমান্ড চালান
            cmd = f'netsh wlan show interface name="{self.interface}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                print(f"⚠️ netsh error: {result.stderr}")
                return WifiSample(rssi_dbm=-80, link_quality=0, timestamp=time.time())
            
            output = result.stdout
            
            # Signal (%) খুঁজুন
            signal_match = re.search(r'Signal\s*:\s*(\d+)%', output)
            # Receive rate (Mbps) খুঁজুন
            rate_match = re.search(r'Receive rate \(Mbps\)\s*:\s*(\d+)', output)
            
            if signal_match:
                quality = int(signal_match.group(1))
                # RSSI = quality * (-0.5) - 50 (পরীক্ষামূলক ফর্মুলা)
                rssi = (quality / 100) * -30 + -50  # 0% → -80, 100% → -50
                
                # রেট দিয়ে আরও নির্ভুল করুন
                if rate_match:
                    rate = int(rate_match.group(1))
                    if rate > 100:
                        rssi = rssi - 5  # ভালো সংযোগে RSSI ভালো হয়
                
                return WifiSample(
                    rssi_dbm=round(rssi, 1),
                    link_quality=quality,
                    timestamp=time.time()
                )
            else:
                print("⚠️ Signal not found in netsh output")
                return WifiSample(rssi_dbm=-80, link_quality=0, timestamp=time.time())
                
        except Exception as e:
            print(f"❌ Error collecting RSSI: {e}")
            return WifiSample(rssi_dbm=-80, link_quality=0, timestamp=time.time())
    
    def start(self):
        """Data collection শুরু করুন"""
        self.running = True
        self.samples = []
        self.thread = threading.Thread(target=self._collect_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Data collection বন্ধ করুন"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def get_samples(self) -> List[WifiSample]:
        """সংগ্রহ করা samples রিটার্ন করুন"""
        return self.samples.copy()
    
    def _collect_loop(self):
        """ব্যাকগ্রাউন্ডে ডেটা সংগ্রহ করুন"""
        while self.running:
            try:
                sample = self.collect_once()
                self.samples.append(sample)
                
                # মেমরি লিমিট (শেষ 1000 স্যাম্পল রাখি)
                if len(self.samples) > 1000:
                    self.samples = self.samples[-1000:]
                
                # sample_rate অনুযায়ী অপেক্ষা
                time.sleep(1.0 / self.sample_rate_hz)
            except Exception as e:
                print(f"❌ Collect loop error: {e}")
                time.sleep(0.5)