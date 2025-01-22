# session.py
import requests
from config import SESSION_URL, API_QUOTE_TOKEN_URL

def create_session_with_password(login, password, remember_me=True):
    payload = {
        "login": login,
        "password": password,
        "remember-me": remember_me
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(SESSION_URL, json=payload, headers=headers)
    if response.status_code in (200, 201):
        data = response.json()['data']
        session_token = data.get("session-token")
        print("Login successful!")
        return session_token
    else:
        raise Exception(f"Error logging in: {response.status_code}, {response.text}")

def get_api_quote_token(session_token):
    headers = {"Authorization": session_token}
    response = requests.get(API_QUOTE_TOKEN_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()["data"]
        token = data.get("token")
        dxlink_url = data.get("dxlink-url")
        print("API Quote Token obtained successfully!")
        return token, dxlink_url
    else:
        raise Exception(f"Error obtaining API Quote Token: {response.status_code}, {response.text}")
