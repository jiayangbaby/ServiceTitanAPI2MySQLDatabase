import requests
import csv
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

AUTH_URL = "https://auth.servicetitan.io/connect/token"
CALLS_URL = "https://api.servicetitan.io/telecom/v3/tenant/{tenant}/calls"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ST_APP_KEY = os.getenv("ST_APP_KEY")
TENANT = os.getenv("TENANT")
OUTPUT_BASE_DIR = os.getenv("OUTPUT_CSV")
OUTPUT_CSV = os.path.join(OUTPUT_BASE_DIR, "calls_data.csv")

# Global token and expiration time
token_info = {
    "access_token": None,
    "expires_at": 0
}

def get_adjusted_time_formatted(weeks=0):
    """
    Returns the adjusted UTC time formatted as YYYY-MM-DDTHH:MM:SSZ.
    Adjusts by the specified number of weeks (positive for future, negative for past).
    """
    current_time = datetime.now(timezone.utc) 
    adjusted_time = current_time + timedelta(weeks=weeks) 
    return adjusted_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_access_token():
    """
    Generates an access token by making a POST request to the auth endpoint.
    """
     # Check if token is still valid
    if time.time() < token_info["expires_at"]:
        return token_info["access_token"]

    print("🔄 Fetching new token...")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(AUTH_URL, headers=headers, data=data)
    if response.status_code == 200:
        data = response.json()
        token_info["access_token"] = data["access_token"]
        token_info["expires_at"] = time.time() + data["expires_in"] - 60  # 1-min buffer
        return token_info["access_token"]
        #return response.json()["access_token"]
    else:
        raise Exception(f"Failed to fetch access token: {response.text}")

def get_jobs_data(access_token, page):
    """
    Fetches jobs data from the ServiceTitan endpoint for a specific page.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ST-App-Key": ST_APP_KEY
    }
    params = {
        "firstAppointmentStartsOnOrAfter": get_adjusted_time_formatted(weeks=-1),
        "direction": "Inbound",
        "page": page,
        "pageSize": 100 
    }
    url = CALLS_URL.replace("{tenant}", TENANT)
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
        
        print("Fetching jobs data...")
        page = 1
        has_more = True
        all_data = []  # json to all data

        while has_more:
            print(f"Fetching page {page}...")
            jobs_data = get_jobs_data(get_access_token(), page)
            
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
