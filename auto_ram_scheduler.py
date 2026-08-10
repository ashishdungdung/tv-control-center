#!/usr/bin/env python3
"""
Sony BRAVIA Automatic Idle RAM Purge Scheduler
----------------------------------------------
Runs in the background and automatically triggers the RAM Cleaner engine
(am kill-all + force-stop idling apps + pm trim-caches 4G)
every N hours when the TV is connected over ADB.
"""

import time
import sys
from ram_cleaner import run_ram_cleaner

DEFAULT_INTERVAL_HOURS = 3

def main():
    interval_hours = DEFAULT_INTERVAL_HOURS
    if len(sys.argv) > 1:
        try:
            interval_hours = float(sys.argv[1])
        except ValueError:
            pass

    interval_seconds = int(interval_hours * 3600)
    print("=" * 65)
    print(f" 🧹 AUTOMATIC IDLE RAM PURGE SCHEDULER STARTED")
    print(f"  Interval: Every {interval_hours} Hours ({interval_seconds} seconds)")
    print(f"  Target Device: 192.168.2.122:5555")
    print("=" * 65)

    while True:
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] ⚡ Executing Scheduled RAM Purge...")
            freed_info = run_ram_cleaner()
            print(f"[{timestamp}] ✅ Scheduled Purge Complete! {freed_info}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during scheduled purge: {e}")
        
        print(f"😴 Sleeping for {interval_hours} hours until next purge cycle...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
