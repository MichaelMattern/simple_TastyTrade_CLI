# config.py
USERNAME = "FILL IN YOUR USERNAME"
PASSWORD = "FILL IN YOUR PASSWORD"

BASE_URL = "https://api.cert.tastyworks.com"
SESSION_URL = f"{BASE_URL}/sessions"
API_QUOTE_TOKEN_URL = f"{BASE_URL}/api-quote-tokens"

ACCOUNT_NUMBER = "5WW84942"
ACCOUNT_NUMBERS = [ACCOUNT_NUMBER]

# NEW: Default market symbols
MARKET_DATA_SYMBOLS = [
    "BTC/USD:CXTALP"
    # Add any other symbols you want to subscribe to by default
]
