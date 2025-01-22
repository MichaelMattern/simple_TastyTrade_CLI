# market_stream.py
import json
import asyncio
import websockets
import keyboard
from config import MARKET_DATA_SYMBOLS  # Import your default symbol list
from session import get_api_quote_token  # if needed

# Module-level state for market stream
is_connected = False

async def stream_market_data(dxlink_url, api_quote_token, symbols=None):
    """
    Connect to the DXLink WebSocket and stream market data.
    
    :param dxlink_url: The WebSocket URL obtained from get_api_quote_token.
    :param api_quote_token: The API quote token used for authorization.
    :param symbols: (Optional) A list of symbols to subscribe to. If None, defaults to MARKET_DATA_SYMBOLS from config.py.
    """
    global is_connected
    
    # If no symbols provided, use default from config
    if symbols is None:
        symbols = MARKET_DATA_SYMBOLS
    
    async with websockets.connect(dxlink_url) as websocket:
        print("Connected to DXLink WebSocket")
        is_connected = True
        try:
            # 1. SETUP
            setup_msg = {
                "type": "SETUP",
                "channel": 0,
                "version": "0.1-DXF-JS/0.3.0",
                "keepaliveTimeout": 60,
                "acceptKeepaliveTimeout": 60
            }
            await websocket.send(json.dumps(setup_msg))
            print("Sent SETUP message")

            setup_response = await websocket.recv()
            print("Received SETUP Response:", setup_response)

            # 2. Wait for AUTH_STATE: UNAUTHORIZED
            auth_state_msg = await websocket.recv()
            print("Received AUTH_STATE:", auth_state_msg)
            auth_state = json.loads(auth_state_msg)
            if auth_state.get("type") != "AUTH_STATE" or auth_state.get("state") != "UNAUTHORIZED":
                raise Exception("Unexpected AUTH_STATE message.")

            # 3. AUTHORIZE using the API quote token
            auth_msg = {
                "type": "AUTH",
                "channel": 0,
                "token": api_quote_token
            }
            await websocket.send(json.dumps(auth_msg))
            print("Sent AUTH message with API Quote Token")

            auth_response = await websocket.recv()
            print("Received AUTH Response:", auth_response)
            auth_response_data = json.loads(auth_response)
            if auth_response_data.get("type") != "AUTH_STATE" or auth_response_data.get("state") != "AUTHORIZED":
                raise Exception("Authorization failed.")

            # 4. CHANNEL_REQUEST
            channel_number = 3
            channel_request_msg = {
                "type": "CHANNEL_REQUEST",
                "channel": channel_number,
                "service": "FEED",
                "parameters": {"contract": "AUTO"}
            }
            await websocket.send(json.dumps(channel_request_msg))
            print(f"Sent CHANNEL_REQUEST for channel {channel_number}")

            channel_open_response = await websocket.recv()
            print("Received CHANNEL_OPENED Response:", channel_open_response)

            # 5. FEED_SETUP
            feed_setup_msg = {
                "type": "FEED_SETUP",
                "channel": channel_number,
                "acceptAggregationPeriod": 0.1,
                "acceptDataFormat": "COMPACT",
                "acceptEventFields": {
                    "Trade": ["eventType", "eventSymbol", "price", "dayVolume", "size"],
                    "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice", "bidSize", "askSize"],
                    "Profile": [
                        "eventType", "eventSymbol", "description", "shortSaleRestriction",
                        "tradingStatus", "statusReason", "haltStartTime", "haltEndTime",
                        "highLimitPrice", "lowLimitPrice", "high52WeekPrice", "low52WeekPrice"
                    ],
                    "Summary": [
                        "eventType", "eventSymbol", "openInterest", "dayOpenPrice",
                        "dayHighPrice", "dayLowPrice", "prevDayClosePrice"
                    ]
                }
            }
            await websocket.send(json.dumps(feed_setup_msg))
            print("Sent FEED_SETUP message")

            feed_setup_response = await websocket.recv()
            print("Received FEED_SETUP Response:", feed_setup_response)

            # 6. FEED_SUBSCRIPTION
            feed_subscription_msg = {
                "type": "FEED_SUBSCRIPTION",
                "channel": channel_number,
                "reset": True,
                "add": []
            }

            for symbol in symbols:
                feed_subscription_msg["add"].extend([
                    {"type": "Trade", "symbol": symbol},
                    {"type": "Quote", "symbol": symbol},
                    {"type": "Profile", "symbol": symbol},
                    {"type": "Summary", "symbol": symbol}
                ])

            await websocket.send(json.dumps(feed_subscription_msg))
            print("Sent FEED_SUBSCRIPTION message:", feed_subscription_msg)

            subscription_response = await websocket.recv()
            print("Received Initial FEED_DATA/Subscription Response:", subscription_response)

            # 7. Keepalive loop
            async def keepalive_loop():
                while is_connected:
                    keepalive_msg = {"type": "KEEPALIVE", "channel": 0}
                    await websocket.send(json.dumps(keepalive_msg))
                    print("Sent KEEPALIVE message")
                    await asyncio.sleep(30)

            keepalive_task = asyncio.create_task(keepalive_loop())

            try:
                while is_connected:
                    if keyboard.is_pressed("esc"):
                        print("\nEsc pressed. Returning to menu...")
                        break
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print("Market Data Received:", json.dumps(data, indent=2))
                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket connection closed")
                        break
            except asyncio.CancelledError:
                print("Stream task cancelled.")
            except Exception as e:
                print("Error:", e)
            finally:
                keepalive_task.cancel()
                try:
                    await keepalive_task
                except asyncio.CancelledError:
                    pass
        finally:
            is_connected = False
            print("Disconnected from WebSocket.")

async def disconnect_stream():
    global is_connected
    if is_connected:
        is_connected = False
        print("Disconnecting from market data stream...")
    else:
        print("No active market data connection to disconnect.")
