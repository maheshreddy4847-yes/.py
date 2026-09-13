class Student:
    def _init_(self, student_id: str, name: str, total_fees: float):
        self.student_id = student_id
        self.name = name
        self.total_fees = float(total_fees)
        self.amount_collected = 0.0
        self.payment_history = []  # Tracks multiple installments

    @property
    def outstanding_amount(self) -> float:
        """Dynamically calculates the remaining unpaid fees."""
        return self.total_fees - self.amount_collected

    @property
    def payment_status(self) -> str:
        """Determines the current payment status."""
        if self.amount_collected == 0:
            return "Unpaid"
        elif self.outstanding_amount > 0:
            return "Partially Paid"
        else:
            return "Fully Paid"

    def make_payment(self, amount: float, date: str):
        """Records a new installment payment with simple bounds checks."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        if amount > self.outstanding_amount:
            raise ValueError(f"Payment of {amount} exceeds outstanding amount of {self.outstanding_amount}")
        
        self.amount_collected += amount
        self.payment_history.append({"amount": amount, "date": date})


class FeeManagementSystem:
    def _init_(self):
        self.students = {}

    def add_student(self, student_id: str, name: str, total_fees: float):
        """Registers a new student profile in the system."""
        if student_id in self.students:
            print(f"Error: Student ID {student_id} already exists.")
            return
        self.students[student_id] = Student(student_id, name, total_fees)

    def record_payment(self, student_id: str, amount: float, date: str):
        """Processes an incoming payment installment for a student."""
        if student_id not in self.students:
            print(f"Error: Student ID {student_id} not found.")
            return
        try:
            self.students[student_id].make_payment(amount, date)
            print(f"Recorded payment of ${amount} for {self.students[student_id].name}.")
        except ValueError as e:
            print(f"Transaction Failed: {e}")

    def get_student_report(self, student_id: str) -> dict:
        """Retrieves history, collection data, and outstanding metric logs."""
        if student_id not in self.students:
            return {"Error": "Student not found"}
        
        student = self.students[student_id]
        return {
            "Student ID": student.student_id,
            "Name": student.name,
            "Total Fees": student.total_fees,
            "Amount Collected": student.amount_collected,
            "Outstanding Amount": student.outstanding_amount,
            "Current Payment Status": student.payment_status,
            "Payment History": student.payment_history
        }

    def identify_students_with_outstanding_fees(self) -> list:
        """Filters and identifies management reports for all students with debt."""
        return [
            {
                "Student ID": s.student_id,
                "Name": s.name,
                "Outstanding Amount": s.outstanding_amount,
                "Status": s.payment_status
            }
            for s in self.students.values() if s.outstanding_amount > 0
        ]


# ==========================================
# Demonstration & Verification
# ==========================================
if __name__ == "_main_":
    # Initialize System
    system = FeeManagementSystem()
    
    # 1. Add students
    system.add_student("STU001", "Alice Vance", 5000.00)
    system.add_student("STU002", "Bob Miller", 4500.00)
    
    # 2. Process split installments (Multiple installments allowed)
    print("--- Recording Payments ---")
    system.record_payment("STU001", 1500.00, "2026-09-01")  # First installment
    system.record_payment("STU001", 2000.00, "2026-09-10")  # Second installment
    system.record_payment("STU002", 4500.00, "2026-09-05")  # Full payment in one go
    
    # 3. Print details for an individual student 
    print("\n--- Student Details Report (Alice) ---")
    alice_report = system.get_student_report("STU001")
    for key, value in alice_report.items():
        print(f"{key}: {value}")
        
    # 4. Identify students with outstanding fees
    print("\n--- Management Alert: Outstanding Dues ---")
    unpaid_list = system.identify_students_with_outstanding_fees()
    for record in unpaid_list:
        print(record)