import pandas as pd
import numpy as np

class SchoolAutomationSystem:
    def _init_(self):
        """Initializes the system with sample scalable data structure."""
        # Simulating a large dataset of students
        data = {
            'student_id': range(1001, 1006),
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            'attendance_rate': [0.92, 0.78, 0.95, 0.82, 0.99],  # Percentage
            'current_gpa': [3.8, 1.9, 3.4, 2.1, 3.9],          # Out of 4.0
            'behavior_flags': [0, 3, 0, 1, 0]                   # Count of incidents
        }
        self.student_df = pd.DataFrame(data)

    def identify_at_risk_students(self, attendance_threshold=0.85, gpa_threshold=2.0, behavior_threshold=2):
        """
        Identifies at-risk students using vectorized operations for maximum optimization.
        Scalability: O(N) time complexity where N is the number of students.
        """
        if self.student_df.empty:
            return pd.DataFrame()

        # Vectorized boolean indexing (highly optimized in C under the hood)
        is_low_attendance = self.student_df['attendance_rate'] < attendance_threshold
        is_low_gpa = self.student_df['current_gpa'] < gpa_threshold
        is_high_behavior_flags = self.student_df['behavior_flags'] >= behavior_threshold

        # Combine conditions using bitwise OR (|)
        at_risk_mask = is_low_attendance | is_low_gpa | is_high_behavior_flags
        
        # Filter dataframe efficiently
        at_risk_students = self.student_df[at_risk_mask].copy()

        # Dynamically assign a risk reason using numpy.select (optimized vector mapping)
        conditions = [
            is_low_attendance & is_low_gpa,
            is_low_attendance,
            is_low_gpa,
            is_high_behavior_flags
        ]
        choices = [
            'Low Attendance & Low GPA',
            'Chronic Absenteeism Risk',
            'Academic Failure Risk',
            'Behavioral Intervention Needed'
        ]
        
        at_risk_students['intervention_reason'] = np.select(conditions, choices, default='General Risk')
        
        return at_risk_students[['student_id', 'name', 'intervention_reason']]

# --- Execution / Demonstration ---
if __name__ == "_main_":
    # Initialize the system
    system = SchoolAutomationSystem()
    
    print("--- Scanning Student Database for At-Risk Profiles ---")
    at_risk_report = system.identify_at_risk_students()
    
    # Display the results
    if not at_risk_report.empty:
        print(at_risk_report.to_string(index=False))
    else:
        print("No at-risk students identified.")