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
TELEGRAM_TOKEN = "7477803057:AAF..."
CHAT_ID = "1848318965"

# === DELTA EXCHANGE SETTINGS ===
DELTA_API_KEY = "your_delta_api_key"
DELTA_SECRET = "your_delta_secret"
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
    url = f"{BASE_URL}/orders"
    timestamp = str(int(time.time() * 1000))

    payload = {
        "product_id": 105,  # ETHUSDT
        "size": qty,
        "side": side,
        "order_type": "market",
        "leverage": LEVERAGE,
    }

    signature = hmac.new(
        bytes(DELTA_SECRET, 'utf-8'),
        msg=bytes(timestamp + "POST/api/v2/orders", 'utf-8'),
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
        send_telegram_alert(f"✅ Trade Executed: {side.upper()} in ETH")
    except Exception as e:
        print("❌ Order Failed:", e)
        send_telegram_alert(f"❌ Trade Failed: {e}")

# === FLASK ROUTES ===
@app.route("/", methods=["GET"])
def home():
    return "ETH TH Bot Running"

@app.route("/trade", methods=["POST"])
def trade():
    data = request.json
    passphrase = data.get("passphrase")
    candles = data.get("candles")  # expects list of last two candles

    if passphrase != "khizar123":
        return {"code": 403, "message": "Unauthorized"}

    if not candles or len(candles) < 2:
        return {"code": 400, "message": "Need 2 candles"}

    candle1 = candles[0]  # previous
    candle2 = candles[1]  # current

    # candle: {"open": float, "close": float, "high": float, "low": float}
    if candle1['close'] < candle1['open'] and candle2['close'] < candle2['open']:
        if candle2['low'] < candle1['low']:
            place_market_order("sell", POSITION_SIZE)
            return {"code": 200, "message": "Sell Executed"}

    elif candle1['close'] > candle1['open'] and candle2['close'] > candle2['open']:
        if candle2['high'] > candle1['high']:
            place_market_order("buy", POSITION_SIZE)
            return {"code": 200, "message": "Buy Executed"}

    return {"code": 200, "message": "No trade condition met"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
