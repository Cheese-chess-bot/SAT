from flask import Flask, render_template_string
import os
import json

app = Flask(__name__)

# --- LAYOUT CONFIG ---
def get_logs():
    if os.path.exists("sat_system.log"):
        with open("sat_system.log", "r") as f:
            return "".join(reversed(f.readlines()[-30:])) # Latest 30 lines
    return "Awaiting system handshake..."

def get_status():
    try:
        with open("medic_status.json", "r") as f:
            return json.load(f)
    except:
        return {"status": "WAITING", "reason": "Initializing Link..."}

@app.route('/')
def home():
    status_data = get_status()
    log_content = get_logs()
    
    # Determine color for the status badge
    status_color = "#39d353" if status_data['status'] == "GO" else "#f85149"
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>S.A.T. COMMAND CENTER</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body { background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', monospace; margin: 0; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #30363d; padding-bottom: 10px; margin-bottom: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
            .panel { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .badge { background: {{ color }}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; }
            .log-stream { background: #010409; border-radius: 8px; padding: 15px; height: 500px; overflow-y: auto; font-family: 'Consolas', monospace; font-size: 12px; line-height: 1.6; color: #8b949e; }
            .stat-val { font-size: 24px; font-weight: bold; color: #58a6ff; margin: 10px 0; }
            h3 { margin-top: 0; color: #f0f6fc; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; }
            .ticker { color: #39d353; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0;">🏥 S.A.T. <span style="color:#58a6ff;">REVENUE ARCHITECT</span></h2>
            <div class="badge">SYSTEM STATE: {{ status }}</div>
        </div>
        <div class="grid">
            <div class="panel">
                <h3>Hardware Medic Status</h3>
                <div class="stat-val">{{ status }}</div>
                <p style="color: #8b949e; font-size: 12px;">Reason: {{ reason }}</p>
                <hr style="border: 0; border-top: 1px solid #30363d; margin: 20px 0;">
                <h3>Active Watchlist</h3>
                <ul style="list-style: none; padding: 0; font-size: 14px;">
                    <li>🔹 <span class="ticker">BTC/USD</span> - Live</li>
                    <li>🔹 <span class="ticker">NVDA</span> - Pre-Market</li>
                    <li>🔹 <span class="ticker">RELIANCE.NS</span> - Open</li>
                </ul>
            </div>
            <div class="panel">
                <h3>Live Master Engine Logs</h3>
                <div class="log-stream">
                    {{ logs | replace('\n', '<br>') | safe }}
                </div>
            </div>
        </div>
        
        <p style="text-align: center; font-size: 10px; color: #484f58; margin-top: 20px;">
            MI300X Forensics v2.4 | Geopolitical Sentinel Active | Port 7860
        </p>
    </body>
    </html>
    """, status=status_data['status'], reason=status_data['reason'], logs=log_content, color=status_color)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860)
