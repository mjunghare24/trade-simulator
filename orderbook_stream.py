import asyncio
import websockets
import json
import time
from models import calculate_slippage, calculate_fees, calculate_market_impact

async def listen():
    url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    async with websockets.connect(url) as websocket:
        while True:
            start = time.perf_counter()
            message = await websocket.recv()
            data = json.loads(message)
            
            # Example processing
            orderbook = {
                "bids": data["bids"],
                "asks": data["asks"]
            }
            quantity = 100  # USD (static for now)
            fee_tier = "tier1"  # static for now

            slippage = calculate_slippage(orderbook, quantity)
            fees = calculate_fees(quantity, fee_tier)
            market_impact = calculate_market_impact(orderbook, quantity)

            net_cost = slippage + fees + market_impact
            latency = time.perf_counter() - start

            print(f"Slippage: {slippage:.4f}, Fees: {fees:.4f}, Impact: {market_impact:.4f}, Net: {net_cost:.4f}, Latency: {latency:.4f}s")

asyncio.run(listen())
