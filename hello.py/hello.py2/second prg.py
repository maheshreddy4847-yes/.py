import os
from src.com.zoho.crm.api.initializer import Initializer
from src.com.zoho.crm.api.dc import USDataCenter # Change center based on your region (e.g., INDataCenter, EUDataCenter)
from src.com.zoho.crm.api.user_signature import UserSignature
from src.com.zoho.crm.api.sdk_config import SDKConfig
from src.com.zoho.crm.api.store import FileStore
from src.com.zoho.crm.api.record import RecordOperations, BodyWrapper, Record, Field
from src.com.zoho.crm.api.util import Choice

class ZohoAdmissionManagement:
    def _init_(self):
        """Initializes the Zoho CRM SDK configuration."""
        logger = None  # Add logging configuration if needed
        
        # User details and OAuth credentials
        user = UserSignature(email="admin@yourdomain.com")
        environment = USDataCenter.PRODUCTION()
        
        # Token store configuration for auto-refreshing access tokens
        token_store = FileStore(file_path="/path/to/zoho_tokens.txt")
        
        config = SDKConfig(auto_refresh_fields=True, pick_list_validation=False)
        resource_path = "/path/to/zoho_sdk_resources"

        # Initialize SDK
        Initializer.initialize(
            user=user,
            environment=environment,
            token_store=token_store,
            sdk_config=config,
            resource_path=resource_path,
            logger=logger
        )

    def capture_webform_enquiry(self, student_first_name, student_last_name, email, phone):
        """Step 1: Capture webform data into the Leads Module."""
        record_ops = RecordOperations()
        request_body = BodyWrapper()
        
        lead = Record()
        lead.add_key_value("First_Name", student_first_name)
        lead.add_key_value("Last_Name", student_last_name)
        lead.add_key_value("Email", email)
        lead.add_key_value("Phone", phone)
        lead.add_key_value("Lead_Source", Choice("Web Content / Form"))
        lead.add_key_value("Lead_Status", Choice("Not Contacted"))
        
        request_body.set_data([lead])
        response = record_ops.create_records("Leads", request_body)
        
        if response:
            action_wrapper = response.get_object()
            for action_response in action_wrapper.get_data():
                if action_response.get_status().get_value() == "success":
                    print(f"Lead successfully created! ID: {action_response.get_details().get('id')}")
                    return action_response.get_details().get('id')
        return None

    def update_follow_up_status(self, lead_id, current_status):
        """Step 2: Manage follow-up status (e.g., Contacted, Attempted to Contact)."""
        record_ops = RecordOperations()
        request_body = BodyWrapper()
        
        lead = Record()
        lead.set_id(int(lead_id))
        lead.add_key_value("Lead_Status", Choice(current_status))
        
        request_body.set_data([lead])
        response = record_ops.update_records("Leads", request_body)
        
        if response:
            print(f"Lead ID {lead_id} follow-up status updated to: {current_status}")

    def finalize_admission(self, lead_id, is_confirmed):
        """
        Step 3 & 4: Confirm or Reject admission.
        If confirmed, convert the Lead to a Contact/Account (Student Process).
        """
        record_ops = RecordOperations()
        
        if not is_confirmed:
            # Reject lead: update status to Lost Lead / Rejected
            self.update_follow_up_status(lead_id, "Lost Lead")
            print(f"Admission rejected. Lead status closed.")
            return

        # Confirm Lead: Convert to Contact (Student Management)
        from src.com.zoho.crm.api.record import ConvertBodyWrapper, LeadConverter
        
        convert_body = ConvertBodyWrapper()
        converter = LeadConverter()
        converter.set_overwrite(True)
        converter.set_assign_to(1234567890) # Replace with the Owner ID
        
        convert_body.set_data([converter])
        response = record_ops.convert_lead(int(lead_id), convert_body)
        
        if response:
            print(f"Admission Confirmed! Lead converted successfully to Student Account.")

# Example Workflow Execution
if __name__ == "__main__":
    crm_system = ZohoAdmissionManagement()
    
    # 1. Simulate entry from Webform
    new_lead_id = crm_system.capture_webform_enquiry(
        student_first_name="Alex", 
        student_last_name="Smith", 
        email="alex.smith@example.com", 
        phone="555-0199"
    )
    
    if new_lead_id:
        # 2. Simulate active follow-up stage
        crm_system.update_follow_up_status(new_lead_id, "Contacted")
        
        # 3. Admission confirmed -> Automatically transitions to Student Management Process
        crm_system.finalize_admission(new_lead_id, is_confirmed=True)