from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# ====== Step 0: Load Environment Variables ======
load_dotenv(dotenv_path='lsa.env')

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
BUSINESS_ID = os.getenv("BUSINESS_ID")
OUTPUT_CSV_PATH = os.getenv("OUTPUT_CSV")  # e.g., C:\Users\jia.wang\OneDrive - hoffmannbros\Desktop\ServiceTitanAPI

# ====== Step 1: Refresh Access Token ======
def get_access_token(client_id, client_secret, refresh_token):
    url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        print("Error details from Google:")
        print(response.text)  # <-- Print out Google's message
        response.raise_for_status()  # Still raise the error so your program knows it's failed

    return response.json()['access_token']

# Get fresh access token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

# ====== Step 2: Pull Lead Reports ======
url = "https://localservices.googleapis.com/v1/leadReports:search"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Pull data from 2024-01-01 to 2025-03-31
body = {
    "query": {
        "accountId": BUSINESS_ID,
        "startDate": {"year": 2024, "month": 1, "day": 1},
        "endDate": {"year": 2025, "month": 3, "day": 31}
    }
}

response = requests.post(url, headers=headers, json=body)

try:
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print("❌ Error occurred!")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    raise e

# Parse leads if no error
data = response.json()
leads = data.get('leadReports', [])

if not leads:
    print("⚠️ No leads found in the specified time range!")
else:
    print(f"✅ Pulled {len(leads)} leads!")

# ====== Step 3: Save Full Leads to CSV ======
df = pd.DataFrame(leads)

# If there's a timestamp field, convert to datetime
if 'createTime' in df.columns:
    df['createTime'] = pd.to_datetime(df['createTime'])

# Create full output file path
full_output_file = os.path.join(OUTPUT_CSV_PATH, 'lsa_leads_stlouis_full.csv')

# Save full raw data
df.to_csv(full_output_file, index=False)
print(f"✅ Full leads saved to {full_output_file}")

# ====== Step 4: Generate Monthly Summary and Save ======
if 'createTime' in df.columns:
    df['month'] = df['createTime'].dt.to_period('M').astype(str)

    summary = df.groupby('month').agg(
        total_leads=('leadId', 'count'),
        total_estimated_job_value=('estimatedJobRevenue', 'sum')
    ).reset_index()

    summary_output_file = os.path.join(OUTPUT_CSV_PATH, 'lsa_leads_summary_by_month.csv')
    summary.to_csv(summary_output_file, index=False)
    print(f"✅ Monthly summary saved to {summary_output_file}")
else:
    print("⚠️ 'createTime' field missing — skipping monthly summary.")





