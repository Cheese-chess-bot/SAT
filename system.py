import os
import time
import psutil
import sys
import subprocess
import requests
import json
import pandas as pd
import pandas_ta as ta
import alpaca_trade_api as tradeapi
import yfinance as yf

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
ALPACA_API_KEY = 'PK7SJ5J7PLCZC2DQ62G7WR6HDM'
ALPACA_SECRET_KEY = 'EzYHuRLoypgLx5uJ2K1B5B2cePPhg2Ubt23ymhH7nbet'
GEMINI_API_KEY = 'AIzaSyDD2qPt_NekjxFtibKebWIWy7mSNdo-m9w'
LOG_FILE = "sat_system.log"

def write_log(message):
    """Writes to terminal and a shared log file for the Web UI."""
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {message}\n")

# ---------------------------------------------------------------------------
# THE SCRAPER & GEMINI MEDIC
# ---------------------------------------------------------------------------
def scrape_system_logs():
    """Scrapes Linux dmesg and ROCm logs for MI300X."""
    try:
        # Grabs the last 20 lines of kernel hardware logs
        dmesg_out = subprocess.check_output(['dmesg', '|', 'tail', '-n', '20'], shell=True, text=True)
    except:
        dmesg_out = "No dmesg available."
    return dmesg_out

def ask_gemini_medic(logs):
    """Sends scraped logs to Gemini for a fix protocol."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"You are an Intel and AMD Hardware Medic. Analyze these kernel logs and provide a 1-sentence Bash fix command. Logs: {logs}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        write_log("ℹ️ [GEMINI] Analyzing scraped logs...")
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
        fix = response.json()['candidates'][0]['content']['parts'][0]['text']
        write_log(f"🪄 [GEMINI FIX] {fix}")
        return fix
    except Exception as e:
        write_log(f"⚠️ [GEMINI ERROR] {e}")
        return "Manual intervention required."

def system_audit():
    """Blocks trade on jitter and triggers scraper if failing."""
    cpu = psutil.cpu_percent(interval=0.1)
    if cpu > 90:
        write_log(f"🚨 [MEDIC] Jitter Detected: CPU {cpu}%. Execution Blocked.")
        logs = scrape_system_logs()
        ask_gemini_medic(logs)
        with open("medic_status.json", "w") as f:
            json.dump({"status": "GO", "time": time.time()}, f)
        return False
    return True
