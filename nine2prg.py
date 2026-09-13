import requests
import json

# --- CONFIGURATION & CREDENTIALS ---
# Replace these with your actual Zoho API credentials
CLIENT_ID = "YOUR_ZOHO_CLIENT_ID"
CLIENT_SECRET = "YOUR_ZOHO_CLIENT_SECRET"
REFRESH_TOKEN = "YOUR_ZOHO_REFRESH_TOKEN"
ZOHO_ACCOUNT_URL = "https://zoho.com"

# Zoho Creator API Endpoint Configuration
# Format: https://zoho.com<account_owner_name>/<app_link_name>/form/<form_link_name>
CREATOR_OWNER = "your_school_org"
CREATOR_APP = "school-parent-portal"
CREATOR_FORM = "Student_Admission_Form"
CREATOR_URL = f"https://zoho.com{CREATOR_OWNER}/{CREATOR_APP}/form/{CREATOR_FORM}"


def get_access_token():
    """Generates a fresh access token using the refresh token."""
    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    try:
        response = requests.post(ZOHO_ACCOUNT_URL, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None


def sync_crm_to_creator(crm_data):
    """
    Pushes data to Zoho Creator.
    Checks for duplicates using a unique identifier (like Lead/Student ID or Email).
    """
    access_token = get_access_token()
    if not access_token:
        print("Failed to authenticate with Zoho.")
        return

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    # 1. Deduplication Check (Search if the student already exists in Creator)
    # Filter by a unique metric like Email or CRM_ID to avoid duplicate data
    unique_email = crm_data.get("Email")
    search_url = f"{CREATOR_URL}?criteria=(Email == \"{unique_email}\")"
    
    try:
        search_response = requests.get(search_url, headers=headers)
        search_response.raise_for_status()
        search_results = search_response.json().get("data", [])
        
        # Mapping CRM Webform fields to Zoho Creator Form field link names
        payload = {
            "data": {
                "Student_Name": crm_data.get("Full_Name"),
                "Email": crm_data.get("Email"),
                "CRM_Lead_ID": crm_data.get("ID"),
                "Admission_Status": crm_data.get("Stage"), # e.g., Lead -> Admission -> Student
                "Academic_Year": crm_data.get("Academic_Year"),
                "Fees_Status": crm_data.get("Fees_Status")
            }
        }

        if search_results:
            # Record exists -> Update important information dynamically
            record_id = search_results[0].get("ID")
            update_url = f"{CREATOR_URL}/{record_id}"
            
            print(f"Record exists (ID: {record_id}). Updating Creator application...")
            update_response = requests.patch(update_url, headers=headers, json=payload)
            update_response.raise_for_status()
            print("Successfully updated existing record.")
            return update_response.json()
            
        else:
            # Record does not exist -> Create new record in Creator Parent Portal
            print("No existing record found. Creating new entry in Creator...")
            create_response = requests.post(CREATOR_URL, headers=headers, json=payload)
            create_response.raise_for_status()
            print("Successfully created new record.")
            return create_response.json()

    except requests.exceptions.RequestException as e:
        print(f"API Error during sync execution: {e}")
        if 'response' in locals() and response is not None:
            print(f"Details: {response.text}")
        return None


# --- SIMULATION RUN ---
if __name__ == "__main__":

    # Mock data coming from a CRM Webform / Lead pipeline entry
    mock_crm_webhook_payload = {
        "ID": "CRM_LEAD_987654321",
        "Full_Name": "Jane Doe",
        "Email": "janedoe@example.com",
        "Stage": "Academic Management",  # Progressing down your flow chart
        "Academic_Year": "2026-2027",
        "Fees_Status": "Paid"
    }

    # Execute sync pipeline
    sync_crm_to_creator(mock_crm_webhook_payload)