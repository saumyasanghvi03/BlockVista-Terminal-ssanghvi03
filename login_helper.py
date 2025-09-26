# login_helper.py
# Run this script locally to generate the access token for Zerodha KiteConnect

import webbrowser
from kiteconnect import KiteConnect
import config  # Import your config.py with API_KEY and API_SECRET

def generate_access_token():
    kite = KiteConnect(api_key=config.API_KEY)
    login_url = kite.login_url()
    print(f"Open this URL in your browser: {login_url}")
    webbrowser.open(login_url)
    
    request_token = input("Enter the request token from the URL after login: ")
    try:
        data = kite.generate_session(request_token, api_secret=config.API_SECRET)
        access_token = data["access_token"]
        print(f"\nAccess Token: {access_token}")
        print("Copy this to config.py or Streamlit secrets.")
    except Exception as e:
        print(f"Error generating session: {e}")

if __name__ == "__main__":
    generate_access_token()
