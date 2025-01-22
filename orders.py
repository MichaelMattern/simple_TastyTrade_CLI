# orders.py
import requests
import json
import keyboard
from datetime import datetime
from config import BASE_URL

def fetch_live_orders(session_token, account_number):
    url = f"{BASE_URL}/accounts/{account_number}/orders/live"
    headers = {"Authorization": session_token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_items = response.json().get("data", {}).get("items", [])
        active_statuses = {"Received", "Live", "Pending", "Working"}
        active_orders = [order for order in all_items if order.get('status') in active_statuses]
        
        if not active_orders:
            print("\n--- No Active Orders Found ---")
            return

        print("\n--- Active Orders ---")
        for order in active_orders:
            print(f"\nOrder ID: {order.get('id')}")
            print(f"Underlying Symbol: {order.get('underlying-symbol')}")
            print(f"Order Type: {order.get('order-type')}")
            print(f"Size: {order.get('size')}")
            print(f"Status: {order.get('status')}")
            print(f"Price: {order.get('price')}")
            print(f"Time-in-Force: {order.get('time-in-force')}")
            print("Legs:")
            for leg in order.get("legs", []):
                print(f"  Symbol: {leg.get('symbol')}")
                print(f"  Action: {leg.get('action')}")
                print(f"  Quantity: {leg.get('quantity')}")
        # Optionally display inactive orders...
    except requests.exceptions.RequestException as e:
        print(f"\nFailed to fetch orders: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")

def submit_order(session_token, account_number):
    url = f"https://api.cert.tastyworks.com/accounts/{account_number}/orders"
    headers = {
        "Authorization": session_token,
        "Content-Type": "application/json"
    }

    # Order type validation
    valid_order_types = {
        "1": "Limit",
        "2": "Market",
        "3": "Stop",
        "4": "Stop Limit",
        "5": "Notional Market"
    }
    print("\nAvailable Order Types:")
    for key, value in valid_order_types.items():
        print(f"{key}. {value}")
    order_type_choice = input("Select order type (enter number): ")
    if order_type_choice not in valid_order_types:
        print("Invalid order type selection.")
        return
    order_type = valid_order_types[order_type_choice]

    # Time in force validation
    valid_tif = {
        "1": "Day",
        "2": "GTC",
        "3": "GTD"
    }
    print("\nAvailable Time-in-Force options:")
    for key, value in valid_tif.items():
        print(f"{key}. {value}")
    tif_choice = input("Select time-in-force (enter number): ")
    if tif_choice not in valid_tif:
        print("Invalid time-in-force selection.")
        return
    time_in_force = valid_tif[tif_choice]

    # Handle GTD date if selected
    gtc_date = None
    if time_in_force == "GTD":
        while True:
            gtc_date = input("Enter the GTD expiration date (YYYY-MM-DD): ")
            try:
                date_obj = datetime.strptime(gtc_date, "%Y-%m-%d")
                if date_obj.date() <= datetime.now().date():
                    print("GTD date must be in the future.")
                    continue
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")

    # Instrument type validation
    valid_instrument_types = {
        "1": "Equity",
        "2": "Equity Option",
        "3": "Future",
        "4": "Cryptocurrency"
    }
    print("\nAvailable Instrument Types:")
    for key, value in valid_instrument_types.items():
        print(f"{key}. {value}")
    instrument_choice = input("Select instrument type (enter number): ")
    if instrument_choice not in valid_instrument_types:
        print("Invalid instrument type selection.")
        return
    instrument_type = valid_instrument_types[instrument_choice]

    # Symbol validation
    symbol = input("\nEnter the instrument symbol (e.g., AAPL, BTC/USD): ").strip().upper()
    if not symbol:
        print("Symbol cannot be empty.")
        return

    # Action validation
    valid_actions = {
        "1": "Buy to Open",
        "2": "Sell to Close",
        "3": "Sell to Open",
        "4": "Buy to Close"
    }
    print("\nAvailable Actions:")
    for key, value in valid_actions.items():
        print(f"{key}. {value}")
    action_choice = input("Select action (enter number): ")
    if action_choice not in valid_actions:
        print("Invalid action selection.")
        return
    action = valid_actions[action_choice]

    # Quantity validation
    while True:
        try:
            quantity = input("\nEnter the order quantity: ")
            if instrument_type == "Cryptocurrency":
                quantity = float(quantity)
                if quantity <= 0:
                    raise ValueError
            else:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError
            break
        except ValueError:
            print("Invalid quantity. Please enter a positive number.")

    # Price validation for limit and stop orders
    price = None
    if order_type in ["Limit", "Stop", "Stop Limit"]:
        while True:
            try:
                price = float(input("\nEnter the price: "))
                if price <= 0:
                    print("Price must be greater than 0.")
                    continue
                break
            except ValueError:
                print("Invalid price. Please enter a valid number.")

    # Price effect validation
    valid_price_effects = {
        "1": "Credit",
        "2": "Debit",
        "3": "None"
    }
    print("\nAvailable Price Effects:")
    for key, value in valid_price_effects.items():
        print(f"{key}. {value}")
    price_effect_choice = input("Select price effect (enter number): ")
    if price_effect_choice not in valid_price_effects:
        print("Invalid price effect selection.")
        return
    price_effect = valid_price_effects[price_effect_choice]

    # Construct order payload
    order_data = {
        "time-in-force": time_in_force,
        "order-type": order_type,
        "price": price if price is not None else None,
        "price-effect": price_effect,
        "legs": [
            {
                "instrument-type": instrument_type,
                "symbol": symbol,
                "action": action,
                "quantity": quantity
            }
        ]
    }

    # Add GTD date if applicable
    if time_in_force == "GTD":
        order_data["gtc-date"] = gtc_date

    # Remove None values from the payload
    order_data = {k: v for k, v in order_data.items() if v is not None}

    # Confirm order details
    print("\n=== Order Details ===")
    print(f"Symbol: {symbol}")
    print(f"Action: {action}")
    print(f"Quantity: {quantity}")
    print(f"Order Type: {order_type}")
    print(f"Time in Force: {time_in_force}")
    if price is not None:
        print(f"Price: ${price}")
    print(f"Price Effect: {price_effect}")
    
    confirm = input("\nConfirm order submission? (y/n): ").lower()
    if confirm != 'y':
        print("Order cancelled.")
        return

    # Submit the order
    try:
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        data = response.json().get("data", {})
        print("\n=== Order Submitted Successfully ===")
        print(f"Order ID: {data.get('order', {}).get('id')}")
        print(f"Status: {data.get('order', {}).get('status')}")
    except requests.exceptions.RequestException as e:
        print(f"\nFailed to submit order: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")


#-----------------------------------------------------------------------------


def cancel_order(session_token, account_number, order_id=None):
    # If no order_id provided, fetch live orders first
    if order_id is None:
        print("\nFetching live orders...")
        fetch_live_orders(session_token, account_number)
        order_id = input("\nEnter the Order ID to cancel (or press Enter to go back): ").strip()
        if not order_id:
            return

    url = f"https://api.cert.tastyworks.com/accounts/{account_number}/orders/{order_id}"
    headers = {
        "Authorization": session_token
    }

    # Confirm cancellation
    confirm = input(f"\nAre you sure you want to cancel order {order_id}? (y/n): ").lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        return

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", {})
        print("\n=== Order Canceled Successfully ===")
        print(f"Order ID: {data.get('id')}")
        print(f"Status: {data.get('status')}")
    except requests.exceptions.RequestException as e:
        print(f"\nFailed to cancel order: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")


#-----------------------------------------------------------------------------------------------------


def cancel_all_orders(session_token, account_number):
    """Cancel all eligible open orders for the given account."""
    url = f"https://api.cert.tastyworks.com/accounts/{account_number}/orders/live"
    headers = {
        "Authorization": session_token
    }

    try:
        # Get all live orders
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_items = response.json().get("data", {}).get("items", [])
        
        # Filter for only active orders
        active_statuses = {"Received", "Live", "Pending", "Working"}
        active_orders = [order for order in all_items if order.get('status') in active_statuses]
        
        if not active_orders:
            print("\nNo active orders found to cancel.")
            return

        # Display active orders that will be cancelled
        print("\n=== Active Orders to Cancel ===")
        for order in active_orders:
            print(f"\nOrder ID: {order.get('id')}")
            print(f"Symbol: {order.get('underlying-symbol')}")
            print(f"Type: {order.get('order-type')}")
            print(f"Status: {order.get('status')}")
            print(f"Price: {order.get('price')}")
            print("------------------------")

        # Confirm cancellation
        total_orders = len(active_orders)
        confirm = input(f"\nAre you sure you want to cancel all {total_orders} active order(s)? (y/n): ").lower()
        if confirm != 'y':
            print("Bulk cancellation aborted.")
            return

        # Cancel each active order
        print("\nCancelling orders...")
        successful_cancels = 0
        failed_cancels = 0

        for order in active_orders:
            order_id = order.get('id')
            try:
                cancel_url = f"https://api.cert.tastyworks.com/accounts/{account_number}/orders/{order_id}"
                cancel_response = requests.delete(cancel_url, headers=headers)
                cancel_response.raise_for_status()
                successful_cancels += 1
                print(f"Successfully cancelled order {order_id}")
            except requests.exceptions.RequestException as e:
                failed_cancels += 1
                print(f"Failed to cancel order {order_id}: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Error details: {e.response.text}")

        # Summary
        print("\n=== Cancellation Summary ===")
        print(f"Total active orders processed: {total_orders}")
        print(f"Successfully cancelled: {successful_cancels}")
        print(f"Failed to cancel: {failed_cancels}")

    except requests.exceptions.RequestException as e:
        print(f"\nFailed to fetch orders: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")


#-----------------------------------------------------------------------------------------------------


def order_manager(session_token, account_number):
    while True:
        print("\n--- Order Manager ---")
        print("1. List Live Orders")
        print("2. Submit New Order")
        print("3. Cancel an Order")
        print("4. Cancel All Orders")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            fetch_live_orders(session_token, account_number)
        elif choice == '2':
            submit_order(session_token, account_number)
        elif choice == '3':
            order_id = input("Enter the Order ID to cancel: ")
            cancel_order(session_token, account_number, order_id)
        elif choice == '4':
            cancel_all_orders(session_token, account_number)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
