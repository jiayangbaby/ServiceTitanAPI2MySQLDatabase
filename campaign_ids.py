import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

AUTH_URL = "https://auth.servicetitan.io/connect/token"
JOBS_URL = "https://api.servicetitan.io/marketing/v2/tenant/{tenant}/campaigns"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ST_APP_KEY = os.getenv("ST_APP_KEY")
TENANT = os.getenv("TENANT")
OUTPUT_BASE_DIR = os.getenv("OUTPUT_CSV")
OUTPUT_CSV = os.path.join(OUTPUT_BASE_DIR, "campaign_ids.csv")

def get_access_token():
    """
    Generates an access token by making a POST request to the auth endpoint.
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(AUTH_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to fetch access token: {response.text}")

def get_campaign_ids(access_token, page):
    """
    Fetches jobs data from the ServiceTitan endpoint for a specific page.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ST-App-Key": ST_APP_KEY
    }
    params = {
        "page": page,
        "pageSize": 100 
    }
    url = JOBS_URL.replace("{tenant}", TENANT)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  
    else:
        raise Exception(f"Failed to fetch appointments data: {response.text}")

def save_to_csv(all_data):
    """
    Saves all accumulated jobs data to a CSV file.
    """
    if not all_data:
        print("No data to save.")
        return

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        headers = all_data[0].keys()
        writer.writerow(headers)
        
        for record in all_data:
            writer.writerow(record.values())
    
    print(f"Data saved to {OUTPUT_CSV}")

def main():
    try:
        print("Generating access token...")
        access_token = get_access_token()
        
        print("Fetching jobs data...")
        page = 1
        has_more = True
        all_data = []  # json to all data

        while has_more:
            print(f"Fetching page {page}...")
            jobs_data = get_campaign_ids(access_token, page)
            
            # add to all data
            all_data.extend(jobs_data.get("data", []))
            
            has_more = jobs_data.get("hasMore", False)
            page += 1 
        
        print("All pages fetched. Writing data to CSV...")
        save_to_csv(all_data)  # write all data to csv at once
        
        print("CSV file successfully updated.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
