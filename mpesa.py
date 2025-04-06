
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import os

# Replace these with your actual Daraja credentials
CONSUMER_KEY = os.getenv("fZ6gwtAISRCnrfFAlhFZHg2lzFINzE9brKvS012B8NrANz7c")
CONSUMER_SECRET = os.getenv("Rt0pF1mcv2ie1fS5dQmACdFqlbHlOiqdPIVFEPNM8ntOKeji5RBn9HQXPt9AwJiZ")
BUSINESS_SHORTCODE = "174379"  #  test shortcode
PASSKEY = os.getenv("bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")  

# URLs
BASE_URL = "https://sandbox.safaricom.co.ke"
TOKEN_URL = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
STK_URL = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
CALLBACK_URL = "https://yourdomain.com/api/mpesa/callback"  # replace with your actual backend callback

def get_access_token():
    response = requests.get(
        TOKEN_URL,
        auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET)
    )
    return response.json().get('access_token')

def lipa_na_mpesa_pochi(phone_number, amount, farmer_number):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",  # Still works with Pochi
        "Amount": amount,
        "PartyA": phone_number,  # vendor phone number
        "PartyB": farmer_number,  # farmer's Pochi number (MSISDN format)
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "SokoHubOrder",
        "TransactionDesc": "Payment for produce"
    }

    response = requests.post(STK_URL, json=payload, headers=headers)
    return response.json()
