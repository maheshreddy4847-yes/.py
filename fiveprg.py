class ExaminationManagement:
    def _init_(self):
        # Nested structure: { student_id: { subject: { exam_name: marks } } }
        self.records = {}
        # Secondary registry to easily track global class performance
        self.students = {}

    def add_student(self, student_id: str, student_name: str):
        """Registers a student into the management system."""
        if student_id not in self.records:
            self.records[student_id] = {}
            self.students[student_id] = student_name

    def enter_marks(self, student_id: str, subject: str, exam_name: str, marks: float, max_marks: float = 100.0):
        """
        Maintains marks across different students, subjects, and examinations.
        Includes validations to prevent faulty data entry.
        """
        # Validation Checks
        if student_id not in self.records:
            raise ValueError(f"Validation Error: Student ID '{student_id}' does not exist.")
        
        if not isinstance(marks, (int, float)) or not isinstance(max_marks, (int, float)):
            raise TypeError("Validation Error: Marks and Maximum Marks must be numeric values.")
            
        if marks < 0 or max_marks <= 0:
            raise ValueError("Validation Error: Marks cannot be negative and maximum marks must be greater than zero.")
            
        if marks > max_marks:
            raise ValueError(f"Validation Error: Obtained marks ({marks}) cannot exceed maximum marks ({max_marks}).")

        # Initializing subject block if it doesn't exist
        if subject not in self.records[student_id]:
            self.records[student_id][subject] = {}

        # Save data as a tuple containing scored marks and total weightage
        self.records[student_id][subject][exam_name] = {
            "obtained": float(marks),
            "max": float(max_marks)
        }

    def get_individual_performance(self, student_id: str) -> dict:
        """Calculates performance summary for a specific student."""
        if student_id not in self.records:
            raise ValueError(f"Student ID '{student_id}' not found.")

        student_data = self.records[student_id]
        performance = {
            "student_name": self.students[student_id],
            "subjects": {},
            "overall_percentage": 0.0
        }

        total_obtained_global = 0.0
        total_max_global = 0.0

        for subject, exams in student_data.items():
            sub_obtained = sum(data["obtained"] for data in exams.values())
            sub_max = sum(data["max"] for data in exams.values())
            
            total_obtained_global += sub_obtained
            total_max_global += sub_max

            performance["subjects"][subject] = {
                "exams_taken": list(exams.keys()),
                "subject_percentage": round((sub_obtained / sub_max) * 100, 2) if sub_max > 0 else 0.0
            }

        if total_max_global > 0:
            performance["overall_percentage"] = round((total_obtained_global / total_max_global) * 100, 2)