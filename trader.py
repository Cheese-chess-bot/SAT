import os, time, psutil,json,requests
import pandas as pd
import pandas_ta_classic as ta 
import alpaca_trade_api as tradeapi 
from flask import Flask
from threading import Thread

# --- 1. HEARTBEAT & MODES ---
server = Flask('')
@server.route('/')
def home(): return f"S.A.T. MEDIC ACTIVE: {os.getenv('TRADE_MODE', 'QUICK')} MODE ⚡"

MODES = {
    "QUICK": {"buy": 45, "sell": 60, "profit": 1.0},
    "SNIPER": {"buy": 35, "sell": 83, "profit": 3.5}
}
CURRENT_MODE = os.getenv('TRADE_MODE', 'QUICK').upper()
m = MODES.get(CURRENT_MODE, MODES["QUICK"])

def print_gemini_insight(log_text):
    """The 'Voice of the System' logic."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key: return # Skip if key isn't set
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = f"Analyze these HFT logs from an AMD MI300X system. Explain in 1 short sentence: Is the hardware safe and the 'Behavioral DNA' clean? Logs: {log_text[-500:]}"
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        insight = response.json()['candidates'][0]['content']['parts'][0]['text']
        print(f"\n🤖 [GEMINI INSIGHT] {insight.strip()}\n", flush=True)
    except: pass
        
# --- 2. THE COMPLETE 20+ PATTERN ENGINE ---
def get_patterns(df):
    if len(df) < 5: return []
    p = []
    
    # Indexing: c=current, c2=previous, c3=3rd back
    c = df.iloc[-1]; c2 = df.iloc[-2]; c3 = df.iloc[-3]
    
    # Core Math
    body = c.close - c.open; abs_body = abs(body)
    upper_wick = c.high - max(c.open, c.close)
    lower_wick = min(c.open, c.close) - c.low
    total_range = c.high - c.low
    avg_body = abs(df['close'] - df['open']).tail(10).mean()

    # Context Math
    body2 = c2.close - c2.open; abs_body2 = abs(body2)
    body3 = c3.close - c3.open; abs_body3 = abs(body3)

    # --- [1-7] SINGLE CANDLE PATTERNS ---
    if abs_body <= (total_range * 0.1): p.append("⚖️ Doji")
    if abs_body > avg_body * 1.5 and upper_wick < (abs_body * 0.1) and lower_wick < (abs_body * 0.1):
        p.append("🚀 Bull Marubozu" if body > 0 else "🚀 Bear Marubozu")
    if lower_wick > (abs_body * 2) and upper_wick < (abs_body * 0.5): 
        p.append("🔨 Hammer" if body > 0 else "👤 Hanging Man")
    if upper_wick > (abs_body * 2) and lower_wick < (abs_body * 0.5): 
        p.append("🏹 Inv Hammer" if body > 0 else "☄️ Shooting Star")
    if abs_body < avg_body and upper_wick > abs_body and lower_wick > abs_body: 
        p.append("🌀 Spinning Top")

    # --- [8-13] DOUBLE CANDLE PATTERNS ---
    if c.close > c2.open and c.open < c2.close and body2 < 0: p.append("📈 Bull Engulfing")
    if c.close < c2.open and c.open > c2.close and body2 > 0: p.append("📉 Bear Engulfing")
    if abs(c.low - c2.low) < (total_range * 0.05): p.append("🖇️ Tweezer Bottom")
    if abs(c.high - c2.high) < (total_range * 0.05): p.append("🖇️ Tweezer Top")
    if c.high < c2.high and c.low > c2.low and body2 < 0: p.append("🤰 Bull Harami")
    if c.high < c2.high and c.low > c2.low and body2 > 0: p.append("🤰 Bear Harami")

    # --- [14-20+] TRIPLE CANDLE PATTERNS ---
    if c.close > c2.close > c3.close and body > 0 and body2 > 0: p.append("💂 3 Soldiers")
    if c.close < c2.close < c3.close and body < 0 and body2 < 0: p.append("🐦 3 Crows")
    if c3.close < c3.open and abs_body2 < (avg_body * 0.5) and body > 0: p.append("🌅 Morning Star")
    if c3.close > c3.open and abs_body2 < (avg_body * 0.5) and body < 0: p.append("🌇 Evening Star")
    if body3 < 0 and c2.high < c3.high and c2.low > c3.low and body > 0 and c.close > c2.high: p.append("⬆️ 3 Inside Up")
    if body3 > 0 and c2.high < c3.high and c2.low > c3.low and body < 0 and c.close < c2.low: p.append("⬇️ 3 Inside Down")
    if abs_body2 < (avg_body * 0.1) and c.open > c2.high and c2.high < c3.low: p.append("👶 Abandoned Baby")

    return p

# --- 3. THE MEDIC ---
def system_audit():
    cpu = psutil.cpu_percent(interval=0.1)
    if cpu > 90:
        write_log(f"⚠️ [MEDIC] Jitter: {cpu}%. Blocked.")
        # NEW LINE: Write STOP to shared link
        with open("medic_status.json", "w") as f:
            json.dump({"status": "STOP", "time": time.time(), "reason": "CPU Jitter"}, f)
        return False

def check_medic_permission():
    try:
        with open("medic_status.json", "r") as f:
            data = json.load(f)
            # Fail-safe: stop if medic is dead (no update for 10s)
            if time.time() - data.get('time', 0) > 10: return False, "Medic Dead"
            return data.get('status') == "GO", data.get('reason', 'N/A')
    except:
        return False, "Link Offline"

# --- 4. MASTER ENGINE ---
def run_sentinel():
    API_KEY = os.getenv('ALPACA_API_KEY')
    SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    alpaca = tradeapi.REST(API_KEY, SECRET_KEY, "https://paper-api.alpaca.markets", api_version='v2')
    
    WATCHLIST = ["BTC/USD", "ETH/USD", "TSLA", "NVDA"]
    print(f"🚀 S.A.T. MEDIC LIVE | Mode: {CURRENT_MODE} | Patterns: 22 Active", flush=True)

    while True:
        # NEW LINK CHECK:
        allowed, reason = check_medic_permission()
        if not allowed:
            print(f"💤 [TRADER] Standby: {reason}", flush=True)
            time.sleep(5)
            continue


        for symbol in WATCHLIST:
            try:
                bars_df = alpaca.get_bars(symbol, "1Min", limit=50).df
                if bars_df.empty: continue
                
                trade = alpaca.get_latest_trade(symbol.replace("/", ""))
                price = trade.price
                rsi = ta.rsi(bars_df['close'], length=14).iloc[-1]
                
                # RE-ENABLED: Full pattern list
                found_patterns = get_patterns(bars_df)
                pat_str = ", ".join(found_patterns) if found_patterns else "Scanning..."

                trade_symbol = symbol.replace("/", "")
                print(f"⚡ [LOG] {trade_symbol: <7} | ${price: >8.2f} | RSI: {rsi:.2f} | {pat_str}", flush=True)

                try:
                    pos = alpaca.get_position(trade_symbol)
                    entry = float(pos.avg_entry_price)
                    profit = ((price - entry) / entry) * 100
                    if profit > m['profit'] or rsi > m['sell']:
                        print(f"💰 EXIT: Selling {trade_symbol} at {profit:.2f}% profit")
                        alpaca.submit_order(symbol=trade_symbol, qty=pos.qty, side='sell', type='market')
                except:
                    if rsi < m['buy']:
                        print(f"🎯 ENTRY: RSI {rsi:.2f} | Buying {trade_symbol}")
                        qty = 0.01 if "USD" in symbol else 1
                        alpaca.submit_order(symbol=trade_symbol, qty=qty, side='buy', type='market')

            except Exception as e: pass 
        time.sleep(60)
if _name_=="_main_":
    run_sentinel
