import re


class Person:
    def __init__(self, name, admission_number):
        self.name = name
        self.admission_number = admission_number

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def admission_number(self):
        return self.__admission_number

    @admission_number.setter
    def admission_number(self, value):
        pattern = r"ADM/\d{4}/\d{3}"
        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid Admission Number Format")
        self.__admission_number = value


class Subject:
    def __init__(self, subject_name, marks):
        self.subject_name = subject_name
        self.marks = marks

    @staticmethod
    def is_valid_mark(value):
        return 0 <= value <= 100

    @property
    def marks(self):
        return self.__marks

    @marks.setter
    def marks(self, value):
        if not Subject.is_valid_mark(value):
            raise ValueError("Marks must be between 0 and 100")
        self.__marks = value

    def has_passed(self):
        return self.marks >= Student.pass_mark


class Student(Person):
    total_students = 0
    pass_mark = 50

    def __init__(self, name, admission_number, subjects):
        super().__init__(name, admission_number)
        self.subjects = subjects
        Student.total_students += 1

    @classmethod
    def get_total_students(cls):
        return cls.total_students

    def calculate_total(self):
        return sum(subject.marks for subject in self.subjects)

    def calculate_average(self):
        return self.calculate_total() / len(self.subjects)

    def determine_grade(self):
        avg = self.calculate_average()

        if avg >= 80:
            return "A"
        elif avg >= 70:
            return "B"
        elif avg >= 60:
            return "C"
        elif avg >= 50:
            return "D"
        else:
            return "E"

    def pass_or_fail(self):
        return "PASS" if self.calculate_average() >= Student.pass_mark else "FAIL"

    def generate_report_card(self):
        print("\n===================================")
        print("Name:", self.name)
        print("Admission No:", self.admission_number)

        for subject in self.subjects:
            print(subject.subject_name, ":", subject.marks)

        print("Total:", self.calculate_total())
        print("Average:", round(self.calculate_average(), 2))
        print("Grade:", self.determine_grade())
        print("Result:", self.pass_or_fail())

    def __str__(self):
        return (f"{self.name} | "
                f"{self.admission_number} | "
                f"Average: {self.calculate_average():.2f}")

    def __lt__(self, other):
        return self.calculate_average() < other.calculate_average()


class HonoursStudent(Student):

    def determine_grade(self):
        avg = self.calculate_average()

        if avg >= 85:
            return "A"
        elif avg >= 75:
            return "B"
        elif avg >= 65:
            return "C"
        elif avg >= 55:
            return "D"
        else:
            return "E"


# Exception handling for invalid marks
try:
    invalid_subject = Subject("Computer Studies", 150)
except ValueError as e:
    print("Error:", e)


# Create students
student1 = Student(
    "John",
    "ADM/2026/001",
    [
        Subject("Mathematics", 80),
        Subject("English", 75),
        Subject("Computer Studies", 90)
    ]
)

student2 = Student(
    "Mary",
    "ADM/2026/002",
    [
        Subject("Mathematics", 65),
        Subject("English", 70),
        Subject("Computer Studies", 68)
    ]
)

student3 = Student(
    "Peter",
    "ADM/2026/003",
    [
        Subject("Mathematics", 50),
        Subject("English", 55),
        Subject("Computer Studies", 60)
    ]
)

student4 = Student(
    "Alice",
    "ADM/2026/004",
    [
        Subject("Mathematics", 40),
        Subject("English", 45),
        Subject("Computer Studies", 50)
    ]
)

student5 = HonoursStudent(
    "Brian",
    "ADM/2026/005",
    [
        Subject("Mathematics", 88),
        Subject("English", 92),
        Subject("Computer Studies", 90)
    ]
)

students = [student1, student2, student3, student4, student5]

# Display report cards
for student in students:
    student.generate_report_card()

# Ranking
best_student = max(students)
weakest_student = min(students)

print("\nBest Performing Student")
print(best_student)

print("\nWeakest Performing Student")
print(weakest_student)

# Total students
print("\nTotal Students Created:",
      Student.get_total_st
