import websocket
import json
import time
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression

# --- Real Models ---

def slippage_model(spread, quantity):
    slippage = 0.0001 + (spread / 1000) + (quantity / 1000000)
    return min(slippage, 0.01)

def fee_model(quantity, fee_tier):
    tier_fees = {
        'tier1': 0.001,
        'tier2': 0.0008,
        'tier3': 0.0006,
    }
    return quantity * tier_fees.get(fee_tier, 0.001)

def market_impact_model(quantity, volatility):
    impact = 0.0002 + 0.0005 * (quantity / 100000) + 0.5 * volatility
    return min(impact, 0.02)

def maker_taker_model(spread, quantity):
    from math import exp
    score = -0.05 + 0.5 * spread - 0.00001 * quantity
    probability = 1 / (1 + exp(-score))
    return probability

# --- WebSocket Logic ---

def start_websocket(ui, asset, quantity_usd, fee_tier):
    ws_url = f"wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/{asset}-SWAP"

    def on_message(ws, message):
        start_time = time.time()

        data = json.loads(message)
        if 'bids' in data and 'asks' in data:
            bids = np.array(data['bids'], dtype=float)
            asks = np.array(data['asks'], dtype=float)

            if bids.size == 0 or asks.size == 0:
                return

            # Calculate best bid/ask and spread
            best_bid = bids[0, 0]
            best_ask = asks[0, 0]
            spread = best_ask - best_bid

            # Approximate volatility using 10 levels (optional refinement)
            try:
                prices = np.concatenate((bids[:, 0], asks[:, 0]))
                volatility = np.std(prices / np.mean(prices))
            except:
                volatility = 0.001

            # Calculate Models
            slippage = slippage_model(spread, quantity_usd)
            fees = fee_model(quantity_usd, fee_tier)
            impact = market_impact_model(quantity_usd, volatility)
            net_cost = slippage + (fees / quantity_usd) + impact
            latency_ms = (time.time() - start_time) * 1000
            maker_prob = maker_taker_model(spread, quantity_usd)

            # Update UI
            ui.update_labels(slippage, fees, impact, net_cost, latency_ms, maker_prob)


    def on_error(ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket Closed")

    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()