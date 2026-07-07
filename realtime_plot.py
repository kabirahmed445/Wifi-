import sys
import time
import matplotlib.pyplot as plt
from collections import deque
sys.path.insert(0, 'archive/v1')

from src.sensing.rssi_collector_win import WindowsWifiCollector

# সেটআপ
plt.ion()  # ইন্টারঅ্যাকটিভ মোড
fig, ax = plt.subplots(figsize=(10, 6))
rssi_data = deque(maxlen=50)  # শেষ ৫০টি ডেটা
time_data = deque(maxlen=50)

collector = WindowsWifiCollector(interface="Wi-Fi", sample_rate_hz=2.0)
collector.start()

print("📡 রিয়েল-টাইম গ্রাফ শুরু হচ্ছে... (বন্ধ করতে Ctrl+C)")
print("💡 রাউটারের কাছে হাঁটুন এবং গ্রাফ দেখুন!")

try:
    while True:
        samples = collector.get_samples()
        if samples:
            latest = samples[-1]
            rssi_data.append(latest.rssi_dbm)
            time_data.append(len(time_data))
            
            ax.clear()
            ax.plot(time_data, rssi_data, 'b-', linewidth=2)
            ax.axhline(y=-50, color='g', linestyle='--', label='Excellent (-50 dBm)')
            ax.axhline(y=-70, color='y', linestyle='--', label='Good (-70 dBm)')
            ax.axhline(y=-80, color='r', linestyle='--', label='Poor (-80 dBm)')
            ax.set_xlabel('Sample Number')
            ax.set_ylabel('RSSI (dBm)')
            ax.set_title('📶 Real-time WiFi RSSI Monitor')
            ax.legend()
            ax.grid(True)
            ax.set_ylim(-90, -40)
            
            plt.pause(0.5)
            print(f"📡 RSSI: {latest.rssi_dbm} dBm | Quality: {latest.link_quality}%", end='\r')
            
except KeyboardInterrupt:
    print("\n⏹️ গ্রাফ বন্ধ করা হচ্ছে...")
finally:
    collector.stop()
    plt.ioff()
    plt.show()