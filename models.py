import numpy as np

# --- Slippage Estimation using simple linear regression approximation ---
def calculate_slippage(orderbook, quantity_usd):
    bids = np.array([[float(price), float(size)] for price, size in orderbook["bids"]])
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"]])

    if len(asks) == 0:
        return 0

    avg_ask_price = np.mean(asks[:, 0])
    depth = np.sum(asks[:, 0] * asks[:, 1])

    # Simple slippage model: Slippage ~ (Quantity / Market Depth)
    slippage = min(quantity_usd / depth, 0.01)  # cap at 1% slippage
    return slippage

# --- Fees Calculation using rule-based model ---
def calculate_fees(quantity_usd, fee_tier):
    fee_tiers = {
        "tier1": 0.0010,  # 0.10%
        "tier2": 0.0008,  # 0.08%
        "tier3": 0.0006,  # 0.06%
    }
    fee_rate = fee_tiers.get(fee_tier.lower(), 0.0010)
    return quantity_usd * fee_rate

# --- Almgren-Chriss Market Impact Model (simplified) ---
def calculate_market_impact(orderbook, quantity_usd):
    bids = np.array([[float(price), float(size)] for price, size in orderbook["bids"]])
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"]])

    if len(asks) == 0 or len(bids) == 0:
        return 0

    mid_price = (asks[0, 0] + bids[0, 0]) / 2
    market_depth = np.sum(asks[:, 0] * asks[:, 1] + bids[:, 0] * bids[:, 1])

    # Simplified Almgren-Chriss: Impact = k * (Quantity / Depth)^alpha
    k = 0.1
    alpha = 0.5
    impact = k * ((quantity_usd / market_depth) ** alpha)
    return min(impact, 0.02)  # Cap at 2% impact

# --- Maker/Taker Logistic Regression Model (Dummy Implementation) ---
def predict_maker_taker(orderbook, quantity_usd):
    # Dummy rule: if quantity is high compared to depth → taker probability high
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"]])
    depth = np.sum(asks[:, 1])

    proportion = 1 / (1 + np.exp(- (quantity_usd / depth - 0.05)))
    return proportion  # returns probability of being taker
