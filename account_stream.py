# account_stream.py
import json
import asyncio
import websockets
import keyboard
import requests
from config import BASE_URL

is_account_stream_connected = False

async def stream_account_data(session_token, account_numbers):
    global is_account_stream_connected
    ws_url = "wss://streamer.cert.tastyworks.com"
    async with websockets.connect(ws_url) as websocket:
        print("Connected to Account Streamer WebSocket")
        is_account_stream_connected = True

        try:
            auth_message = {
                "action": "connect",
                "value": account_numbers,
                "auth-token": session_token,
                "request-id": 1
            }
            await websocket.send(json.dumps(auth_message))
            print("Sent authentication message:", auth_message)

            auth_response = await websocket.recv()
            print("Authentication response received:", auth_response)

            async def send_heartbeat():
                while is_account_stream_connected:
                    heartbeat_message = {
                        "action": "heartbeat",
                        "auth-token": session_token,
                        "request-id": 2
                    }
                    await websocket.send(json.dumps(heartbeat_message))
                    print("Sent heartbeat message")
                    await asyncio.sleep(3)

            heartbeat_task = asyncio.create_task(send_heartbeat())

            try:
                while is_account_stream_connected:
                    if keyboard.is_pressed("esc"):
                        print("\nEsc key pressed. Disconnecting from account stream...")
                        break
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if data.get("type") == "AccountBalance":
                            print("\nAccount Balance Update:")
                            print(json.dumps(data["data"], indent=2))
                        else:
                            print("Account Data Received:", json.dumps(data, indent=2))
                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket connection closed")
                        break
            except asyncio.CancelledError:
                print("Account stream task cancelled.")
            except Exception as e:
                print("Error in account data stream:", e)
            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
        finally:
            is_account_stream_connected = False
            print("Disconnected from Account Streamer WebSocket.")

def fetch_account_balances(session_token, account_number):
    url = f"{BASE_URL}/accounts/{account_number}/balances"
    headers = {"Authorization": session_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {})
        print("\n--- Account Balance ---")
        print(f"Account Number: {data.get('account-number')}")
        print(f"Net Liquidating Value: {data.get('net-liquidating-value')}")
        print(f"Cash Balance: {data.get('cash-balance')}")
        print(f"Long Equity Value: {data.get('long-equity-value')}")
        print(f"Short Equity Value: {data.get('short-equity-value')}")
        print(f"Equity Buying Power: {data.get('equity-buying-power')}")
        print(f"Derivative Buying Power: {data.get('derivative-buying-power')}")
        print(f"Cash Available to Withdraw: {data.get('cash-available-to-withdraw')}")
    else:
        print(f"Failed to fetch account balances: {response.status_code} {response.text}")

def fetch_account_positions(session_token, account_number):
    url = f"{BASE_URL}/accounts/{account_number}/positions"
    headers = {"Authorization": session_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("data", {}).get("items", [])
        if not items:
            print("\n--- No Positions Found ---")
            return

        print("\n--- Account Positions ---")
        for position in items:
            print(f"\nSymbol: {position.get('symbol')}")
            print(f"Instrument Type: {position.get('instrument-type')}")
            print(f"Quantity: {position.get('quantity')} ({position.get('quantity-direction')})")
            print(f"Close Price: {position.get('close-price')}")
            print(f"Average Open Price: {position.get('average-open-price')}")
            print(f"Unrealized Day Gain: {position.get('realized-day-gain')}")
            print(f"Realized Today: {position.get('realized-today')}")
            print(f"Updated At: {position.get('updated-at')}")
    else:
        print(f"Failed to fetch account positions: {response.status_code} {response.text}")
