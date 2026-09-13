import datetime
import requests
  

# Configuration Variables
CLIENT_ID = "YOUR_ZOHO_CLIENT_ID"
CLIENT_SECRET = "YOUR_ZOHO_CLIENT_SECRET"
REFRESH_TOKEN = "YOUR_ZOHO_REFRESH_TOKEN"
API_DOMAIN = "https://zohoapis.com"  # Change to .eu, .in, etc., based on your region


def get_access_token():
    """Generates a fresh access token using the refresh token."""
    url = f"https://zoho.com"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to fetch access token: {response.text}")


def record_attendance(student_id, date_str, status):
    """
    Records daily student attendance in the 'Attendance' Custom Module.
    Prevents duplicates by creating and enforcing a unique composite key.
    """
    access_token = get_access_token()
    url = f"{API_DOMAIN}/crm/v3/Attendance"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json",
    }

    # Generate a unique key (e.g., "STU101_2026-09-13")
    # Zoho CRM will block the insert if this key already exists, preventing duplicates.
    unique_key = f"{student_id}_{date_str}"

    payload = {
        "data": [
            {
                "Student_ID": student_id,
                "Attendance_Date": date_str,
                "Status": status,
                "Unique_Attendance_Key": unique_key,
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Successfully recorded attendance for Student {student_id}.")
        return response.json()
    elif response.status_code == 202:
        # Handles cases where duplication settings catch an error or update triggers
        print(f"Warning/Duplicate detected for Student {student_id}: {response.json()}")
        return response.json()
    else:
        print(f"Error recording attendance: {response.status_code} - {response.text}")
        return None


def get_student_attendance_percentage(student_id):
    """
    Fetches the entire attendance history for a specific student
    and calculates their current overall attendance percentage.
    """
    access_token = get_access_token()
    # Criteria search to pull records matching the student ID
    url = f"{API_DOMAIN}/crm/v3/Attendance/search"

    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    params = {"criteria": f"(Student_ID:equals:{student_id})"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 204:
        print(f"No attendance history found for Student {student_id}.")
        return 0.0
    elif response.status_code == 200:
        records = response.json().get("data", [])
        total_days = len(records)
        days_present = sum(
            1 for record in records if record.get("Status") == "Present"
        )

        if total_days == 0:
            return 0.0

        attendance_percentage = (days_present / total_days) * 100
        print(f"Student ID: {student_id}")
        print(f"Total Days Tracked: {total_days} | Days Present: {days_present}")
        print(f"Attendance Rate: {attendance_percentage:.2f}%")

        return attendance_percentage
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        return None


# --- Example Executions ---
if __name__ == "_main_":
    # 1. Record daily attendance for a student (Today's date)
    today = datetime.date.today().strftime("%Y-%m-%d")
    record_attendance(
        student_id="STU1001", date_str=today, status="Present"
    )

    # 2. Try recording a duplicate to test prevention rules
    print("\nAttempting to write a duplicate record to check system safety...")
    record_attendance(
        student_id="STU1001", date_str=today, status="Present"
    )

    # 3. Calculate and display management analytics for a student
    print("\nFetching data for management dashboard view...")
    get_student_attendance_percentage(student_id="STU1001")