import sys
import os

# Python পাথ সেট করা
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'archive/v1'))

from src.sensing.rssi_collector import WindowsWifiCollector

# WiFi সেন্সর চালানো
collector = WindowsWifiCollector(interface='Wi-Fi')
sample = collector.collect_once()

print(f"📡 RSSI: {sample.rssi_dbm} dBm")
print(f"📶 Quality: {sample.link_quality:.0%}")