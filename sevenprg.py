import requests
import json

# ==========================================
# 1. CONFIGURATION & CREDENTIALS
# ==========================================
# Replace these placeholder values with your official Zoho API credentials
CLIENT_ID = "YOUR_ZOHO_CLIENT_ID"
CLIENT_SECRET = "YOUR_ZOHO_CLIENT_SECRET"
REFRESH_TOKEN = "YOUR_ZOHO_REFRESH_TOKEN"

# Zoho Environment Domains (Change to .eu, .in, etc., if your account is not .com)
ACCOUNTS_URL = "https://zoho.com"
CRM_API_URL = "https://zohoapis.com"
CREATOR_API_URL = "https://zoho.com"

# Zoho Creator Target Details
CREATOR_OWNER = "YOUR_ZOHO_ACCOUNT_OWNER_EMAIL"
CREATOR_APP_LINK_NAME = "parent_application"
CREATOR_REPORT_LINK_NAME = "Student_Details_Report"

# ==========================================
# 2. ACCESS TOKEN GENERATION
# ==========================================
def get_access_token():
    """Generates a fresh, short-lived IAM access token using the Refresh Token."""
    payload = {
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(ACCOUNTS_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        if "access_token" in token_data:
            return token_data["access_token"]
        else:
            raise KeyError(f"Access token missing in response: {token_data}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating with Zoho accounts: {e}")
        return None

# ==========================================
# 3. CRM DATA RETRIEVAL (PARENT-CHILD MATCH)
# ==========================================
def fetch_student_crm_data(access_token, parent_email):
    """
    Searches Zoho CRM for the Contact/Student record associated with the parent email.
    Enforces record-level security by filtering strictly by logged-in parent email.
    """
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    # Query parameters to look up the student based on Parent Email field
    # (Adjust 'Parent_Email' to match your actual custom field API name in CRM Contacts)
    params = {
        "criteria": f"(Parent_Email:equals:{parent_email})"
    }
    
    try:
        # Assuming Student data lives in the 'Contacts' module of your Zoho CRM
        url = f"{CRM_API_URL}/Contacts"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 204:
            print("No matching student profile found for this parent email in CRM.")
            return None
            
        response.raise_for_status()
        crm_data = response.json()
        
        # Extract the first matching student record
        student_record = crm_data.get("data", [{}])[0]
        return student_record

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Zoho CRM: {e}")
        return None

# ==========================================
# 4. CREATOR SYNCHRONIZATION
# ==========================================
def sync_data_to_creator_view(access_token, student_crm_id):
    """
    Retrieves or validates synchronized student data from Zoho Creator Report
    filtered securely by the unique Student ID.
    """
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    # Securely filter creator data so the parent only pulls records matching their child's CRM ID
    # (Adjust 'CRM_Student_ID' to match your field link name in Creator)
    url = f"{CREATOR_API_URL}/{CREATOR_OWNER}/{CREATOR_APP_LINK_NAME}/report/{CREATOR_REPORT_LINK_NAME}"
    params = {
        "criteria": f'(CRM_Student_ID == "{student_crm_id}")'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 204:
            print("No synchronized data found in Creator for this student ID.")
            return None
            
        response.raise_for_status()
        creator_data = response.json()
        return creator_data.get("data", [])

    except requests.exceptions.RequestException as e:
        print(f"Error accessing Zoho Creator App: {e}")
        return None

# ==========================================
# 5. EXECUTION PIPELINE
# ==========================================
if __name__ == "_main_":
    # Simulate a logged-in parent session email
    LOGGED_IN_PARENT_EMAIL = "parent@example.com"
    
    print("Initiating Zoho Sync Service...")
    token = get_access_token()
    
    if token:
        print("Authentication Successful. Fetching secure CRM Data...")
        student_profile = fetch_student_crm_data(token, LOGGED_IN_PARENT_EMAIL)
        
        if student_profile:
            student_id = student_profile.get("id")
            print(f"Successfully verified child record. Student CRM ID: {student_id}")
            print(f"Student Name: {student_profile.get('Full_Name')}")
            
            print("\nPulling isolated Creator App dashboard data...")
            child_dashboard_data = sync_data_to_creator_view(token, student_id)
            
            if child_dashboard_data:
                print("\n--- Parent Application Dashboard Data ---")
                print(json.dumps(child_dashboard_data, indent=4))
            else:
                print("Failed to pull live Creator details.")
        else:
            print("Access Denied: No student mapping found for this email identifier.")
    else:
        print("Synchronization stopped due to an authentication error.")