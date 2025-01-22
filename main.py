# main.py
import asyncio
from config import (
    USERNAME,
    PASSWORD,
    ACCOUNT_NUMBER,
    ACCOUNT_NUMBERS,
    MARKET_DATA_SYMBOLS  # <--- Import the default symbol list
)
from session import create_session_with_password, get_api_quote_token
from market_stream import stream_market_data, disconnect_stream, is_connected
from account_stream import stream_account_data, fetch_account_balances, fetch_account_positions
from orders import order_manager

def menu():
    global USERNAME, PASSWORD
    while True:
        print("\n--- Account Management Menu ---")
        print("1. Connect to Market Data Stream")
        print("2. Connect to Account Stream")
        print("3. List Account Balances")
        print("4. List Account Positions")
        print("5. Order Manager")
        print("6. Disconnect from Streams")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            if not is_connected:
                try:
                    session_token = create_session_with_password(USERNAME, PASSWORD)
                    api_quote_token, dxlink_url = get_api_quote_token(session_token)
                    
                    # Use the default list of symbols from config.py
                    asyncio.run(stream_market_data(dxlink_url, api_quote_token, MARKET_DATA_SYMBOLS))
                except Exception as e:
                    print(f"Error connecting to market stream: {e}")
            else:
                print("Already connected to the market data stream.")
        
        elif choice == '2':
            try:
                session_token = create_session_with_password(USERNAME, PASSWORD)
                # Use your configured list of account numbers
                asyncio.run(stream_account_data(session_token, ACCOUNT_NUMBERS))
            except Exception as e:
                print(f"Error connecting to account stream: {e}")
        
        elif choice == '3':
            session_token = create_session_with_password(USERNAME, PASSWORD)
            # Use your configured single account number
            fetch_account_balances(session_token, ACCOUNT_NUMBER)
        
        elif choice == '4':
            session_token = create_session_with_password(USERNAME, PASSWORD)
            # Use your configured single account number
            fetch_account_positions(session_token, ACCOUNT_NUMBER)
        
        elif choice == '5':
            session_token = create_session_with_password(USERNAME, PASSWORD)
            # Use your configured single account number
            order_manager(session_token, ACCOUNT_NUMBER)
        
        elif choice == '6':
            asyncio.run(disconnect_stream())
        
        elif choice == '7':
            if is_connected:
                asyncio.run(disconnect_stream())
            print("Exiting program.")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nExiting program.")
