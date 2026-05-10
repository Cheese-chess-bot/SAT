import subprocess
import time
import os
import sys

# Ensure the current directory is in the path so it can find sat_dashboard
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard import app 

def boot_sentinel_suite():
    # 1. Start the Hardware Medic Scraper (Background)
    print("🏥 [BOOT] Launching S.A.T. Medic Scraper...")
    subprocess.Popen(["python3", "system.py"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    # 2. Start the Trading Sentinel (Background)
    print("🚀 [BOOT] Launching S.A.T. Trader Sentinel...")
    subprocess.Popen(["python3", "trader.py"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    # Initialize the log file if it doesn't exist so the UI doesn't crash
    if not os.path.exists("sat_system.log"):
        with open("sat_system.log", "w") as f:
            f.write("[SYSTEM] Initializing S.A.T. Master Engine...\n")
            
    boot_sentinel_suite()
    
    # 3. Start Dashboard on Port 7860 (Mandatory for HF)
    print("🌐 [BOOT] Dashboard Live on Port 7860")
    app.run(host='0.0.0.0', port=7860)
