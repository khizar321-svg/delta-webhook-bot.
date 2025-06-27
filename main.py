from flask import Flask, request
import requests

app = Flask(__name__)

DELTA_API_KEY = "YOUR_DELTA_API_KEY"
DELTA_SECRET = "YOUR_DELTA_SECRET"
SYMBOL = "ETHUSDT"
LEVERAGE = 25

def place_market_order(side, qty):
    print(f"Placing {side} order for {qty} ETH with leverage {LEVERAGE}")
    # NOTE: Actual API call to Delta Exchange will go here

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data['passphrase'] != "khizar123":
        return {"code": 403, "message": "Invalid passphrase"}

    signal = data['signal']
    if signal == "buy":
        place_market_order("buy", 1)
    elif signal == "sell":
        place_market_order("sell", 1)

    return {"code": 200, "message": "Order placed"}

if __name__ == "__main__":
    app.run()
  
