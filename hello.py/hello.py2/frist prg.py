from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional


# ==========================================
# ENUMS & CONSTANTS
# ==========================================
class AdmissionStatus(Enum):
    APPLIED = "Applied"
    UNDER_REVIEW = "Under Review"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    ENROLLED = "Enrolled"


class AttendanceStatus(Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"


class FeeStatus(Enum):
    UNPAID = "Unpaid"
    PARTIALLY_PAID = "Partially Paid"
    PAID = "Paid"
    OVERDUE = "Overdue"


# ==========================================
# MODULE 1: ZOHO CRM (Internal Backend)
# ==========================================

class AdmissionRecord:
    """Manages new applicant details and processing pipeline."""
    def _init_(self, applicant_id: str, student_name: str, grade_applied: str, submission_date: date):
        self.applicant_id: str = applicant_id
        self.student_name: str = student_name
        self.grade_applied: str = grade_applied
        self.submission_date: date = submission_date
        self.status: AdmissionStatus = AdmissionStatus.APPLIED
        self.notes: Optional[str] = None

    def update_status(self, new_status: AdmissionStatus):
        self.status = new_status


class StudentProfile:
    """Core Student module tracking academic profiles."""
    def _init_(self, student_id: str, first_name: str, last_name: str, date_of_birth: date, grade_level: str):
        self.student_id: str = student_id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.date_of_birth: date = date_of_birth
        self.grade_level: str = grade_level
        self.parent_id: Optional[str] = None  # Links to Zoho Creator Parent App User
        self.courses_enrolled: List[str] = []


class AcademicCourse:
    """Manages school subjects, teachers, and class schedules."""
    def _init_(self, course_id: str, course_name: str, teacher_name: str, room: str):
        self.course_id: str = course_id
        self.course_name: str = course_name
        self.teacher_name: str = teacher_name
        self.room: str = room


class AttendanceLog:
    """Tracks mandatory regular student class attendance."""
    def _init_(self, student_id: str, attendance_date: date, status: AttendanceStatus):
        self.student_id: str = student_id
        self.attendance_date: date = attendance_date
        self.status: AttendanceStatus = status


class ExaminationRecord:
    """Stores exam modules, marks achieved, and weightage."""
    def _init_(self, student_id: str, course_id: str, exam_name: str, max_marks: float, marks_obtained: float):
        self.student_id: str = student_id
        self.course_id: str = course_id
        self.exam_name: str = exam_name
        self.max_marks: float = max_marks
        self.marks_obtained: float = marks_obtained
        self.percentage: float = (marks_obtained / max_marks) * 100


class FeeStructure:
    """Tracks school tuition balances, invoices, and payments."""
    def _init_(self, invoice_id: str, student_id: str, total_amount: float, due_date: date):
        self.invoice_id: str = invoice_id
        self.student_id: str = student_id
        self.total_amount: float = total_amount
        self.amount_paid: float = 0.0
        self.due_date: date = due_date
        self.status: FeeStatus = FeeStatus.UNPAID

    def record_payment(self, payment_amount: float):
        self.amount_paid += payment_amount
        if self.amount_paid >= self.total_amount:
            self.status = FeeStatus.PAID
        elif self.amount_paid > 0:
            self.status = FeeStatus.PARTIALLY_PAID


# ==========================================
# MODULE 2: ZOHO CREATOR (Parent Interface App)
# ==========================================

class ZohoCreatorParentPortal:
    """ Parent Portal UI mirroring subsets of backend Zoho CRM data safely. """
    def _init_(self, parent_id: str, primary_contact: str):
        self.parent_id: str = parent_id
        self.primary_contact: str = primary_contact
        self.linked_students: List[str] = []  # List of Student IDs

    def view_child_dashboard(self, student_id: str, database: Dict) -> Dict:
        """Integration layer query combining multiple CRM structures into one clean API layout."""
        if student_id not in self.linked_students:
            return {"Error": "Unauthorized access to student record."}
            
        student: StudentProfile = database["students"].get(student_id)
        attendance: List[AttendanceLog] = [log for log in database["attendance"] if log.student_id == student_id]
        exams: List[ExaminationRecord] = [ex for ex in database["examinations"] if ex.student_id == student_id]
        fees: List[FeeStructure] = [f for f in database["fees"] if f.student_id == student_id]

        return {
            "Student Name": f"{student.first_name} {student.last_name}",
            "Grade": student.grade_level,
            "Recent Attendance Logs": [{"Date": log.attendance_date.isoformat(), "Status": log.status.value} for log in attendance],
            "Exam Performance": [{"Subject": ex.course_id, "Exam": ex.exam_name, "Grade": f"{ex.percentage:.2f}%"} for ex in exams],
            "Outstanding Invoices": [{"InvoiceID": f.invoice_id, "Balance Due": f.total_amount - f.amount_paid, "Status": f.status.value} for f in fees]
        }


# ==========================================
# DATA INTEGRATION & VALIDATION RUNTIME
# ==========================================
if __name__ == "_main_":
    # Simulated centralized relational database context
    mock_db = {
        "admissions": {},
        "students": {},
        "courses": {},
        "attendance": [],
        "examinations": [],
        "fees": []
    }

    # 1. Populate Zoho CRM data
    student_john = StudentProfile("STU-101", "John", "Doe", date(2015, 5, 20), "Grade 5")
    mock_db["students"]["STU-101"] = student_john

    # Add Attendance log
    mock_db["attendance"].append(AttendanceLog("STU-101", date(2026, 9, 11), AttendanceStatus.PRESENT))
    mock_db["attendance"].append(AttendanceLog("STU-101", date(2026, 9, 12), AttendanceStatus.LATE))

    # Add Academic Exam Data
    mock_db["examinations"].append(ExaminationRecord("STU-101", "MATH-5", "Midterm Term 1", 100, 88.5))

    # Add Billing Info
    term1_fee = FeeStructure("INV-2026-01", "STU-101", 1500.00, date(2026, 10, 1))
    term1_fee.record_payment(500.00)  # Partially paid
    mock_db["fees"].append(term1_fee)

    # 2. Access through Zoho Creator Parent Application Portal Linkage
    parent_portal = ZohoCreatorParentPortal(parent_id="PAR-909", primary_contact="parent.doe@email.com")
    parent_portal.linked_students.append("STU-101")  # Relational mapping

    # Pulling data via client layer interface integration API
    johns_dashboard_view = parent_portal.view_child_dashboard("STU-101", mock_db)
    
    # Print clean diagnostic output view
    print(f"--- Parent Dashboard View Generated via Zoho Creator App ---")
    import json
    print(json.dumps(johns_dashboard_view, indent=4))