class AcademicYear:
    def _init_(self, name):
        self.name = name
        self.classes = []

    def add_class(self, cls):
        self.classes.append(cls)


class Subject:
    def _init_(self, name):
        self.name = name


class Teacher:
    def _init_(self, name):
        self.name = name
        self.subjects = []

    def assign_subject(self, subject):
        self.subjects.append(subject)


class Section:
    def _init_(self, name):
        self.name = name
        self.students = []
        self.teacher_subject_assignments = {}  # Format: {Subject: Teacher}

    def add_student(self, student):
        self.students.append(student)
        student.section = self

    def assign_teacher_for_subject(self, teacher, subject):
        self.teacher_subject_assignments[subject] = teacher


class SchoolClass:
    def _init_(self, name):
        self.name = name
        self.sections = []

    def add_section(self, section):
        self.sections.append(section)


class Student:
    def _init_(self, name):
        self.name = name
        self.section = None


# ==========================================
# TEST DEMONSTRATION & RELATIONSHIP MAPPING
# ==========================================

# 1. Create Core Records (Academic Year, Subjects, Teachers)
year_2026 = AcademicYear("2026-2027")

math = Subject("Mathematics")
science = Subject("Science")

mr_smith = Teacher("Mr. Smith")
ms_davis = Teacher("Ms. Davis")

mr_smith.assign_subject(math)
ms_davis.assign_subject(science)

# 2. Create Class and Sections
grade_10 = SchoolClass("Grade 10")
section_a = Section("A")

grade_10.add_section(section_a)
year_2026.add_class(grade_10)

# 3. Associate Teachers & Subjects to the Section
section_a.assign_teacher_for_subject(mr_smith, math)
section_a.assign_teacher_for_subject(ms_davis, science)

# 4. Enroll Students into Class and Section
alice = Student("Alice Smith")
bob = Student("Bob Jones")

section_a.add_student(alice)
section_a.add_student(bob)

# ==========================================
# QUERY SYSTEM (Understanding Student Associations)
# ==========================================

print(f"--- Academic Query Report for {year_2026.name} ---")

for cls in year_2026.classes:
    for sec in cls.sections:
        print(f"\nClass: {cls.name} | Section: {sec.name}")
        print("-" * 35)
        
        # Display Students belonging to this specific Class and Section
        print("Enrolled Students:")
        for student in sec.students:
            print(f"  - {student.name}")
            
        # Display Associated Teachers and Subjects
        print("\nAssigned Faculty & Subjects:")
        for subj, teach in sec.teacher_subject_assignments.items():
            print(f"  - {subj.name} is taught by {teach.name}")