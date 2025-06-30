from flask import Flask, request
import requests
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime

app = Flask(__name__)

# === TELEGRAM SETTINGS ===
TELEGRAM_TOKEN = "7477803057:AAFxjKe53WtU6FMr2W-WcmV3baMFcBUx6WA"
CHAT_ID = "1848318965"

# === DELTA EXCHANGE SETTINGS ===
DELTA_API_KEY = "zAdaSnIRpprW4KQ1IRwU405d8BByNF...1"
DELTA_SECRET = "MnFknDS39J3h2U31CrdY07T4k3TuHAqo0yNJ7hjnC4uFnWBb912DK82QyBRy... secret"
BASE_URL = "https://api.delta.exchange"

# === BOT SETTINGS ===
SYMBOL = "ETHUSDT"
LEVERAGE = 25
POSITION_SIZE = 1  # in ETH
TP_PERCENT = 0.15

# === SEND TELEGRAM ALERT ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("❌ Telegram alert failed:", e)

# === PLACE MARKET ORDER ===
def place_market_order(side, qty):
    url = "https://api.delta.exchange/orders"
    timestamp = str(int(time.time()))

    payload = {
        "product_id": 105,  # ETHUSDT
        "size": qty,
        "side": side,
        "order_type": "market",
        "leverage": LEVERAGE,
    }

    signature = hmac.new(
        bytes(DELTA_SECRET, 'utf-8'),
        msg=bytes(timestamp + "POST/api/v2/orders" + json.dumps(payload), 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {
        "api-key": DELTA_API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        print("✅ Order Placed:", res.json())
        send_telegram_alert(f"✅ Trade executed: {side.upper()} {qty} ETH")
    except Exception as e:
        print("❌ Order Failed:", e)
        send_telegram_alert(f"❌ Trade failed: {side.upper()} ETH — {str(e)}")

    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.json())
    ):
    # Example logic only - you must implement Delta API signature etc.
    send_telegram_alert(f"\U0001F4B8 {side.upper()} Order Placed at ${entry_price:.2f}")

    # Calculate 15% TP
    if side == "buy":
        target_price = entry_price * (1 + TP_PERCENT)
        sl = entry_price * 0.98  # Simulated SL 2% below
    else:
        target_price = entry_price * (1 - TP_PERCENT)
        sl = entry_price * 1.02

    send_telegram_alert(f"\U0001F3AF Target set at ${target_price:.2f} | Stoploss at ${sl:.2f}")
    
    # Simulate TP hit after 1 minute (you should use real-time price tracking)
    time.sleep(5)
    send_telegram_alert("\U0001F389 15% Target Hit: 80% position exited!")
    time.sleep(5)
    send_telegram_alert("\U0001F51A Remaining 20% exited at candle close")

@app.route("/", methods=["GET"])
def home():
    return "ETH 1H Bot Running"

@app.route("/trade", methods=["POST"])
def trade():
    data = request.json
    passphrase = data.get("passphrase")
    signal = data.get("signal")
    price = float(data.get("price"))

    if passphrase != "khizar123":
        return {"code": 403, "message": "Invalid passphrase"}, 403

    if signal == "buy":
        place_market_order("buy", price)
    elif signal == "sell":
        place_market_order("sell", price)
    else:
        return {"code": 400, "message": "Invalid signal"}, 400

    return {"code": 200, "message": "Trade executed"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
