from dataclasses import dataclass, field
from typing import List, Dict
from PIL import Image


@dataclass
class QuestionTypeOption:
    name: str
    statements: list = field(default_factory=list)

@dataclass
class QuestionType:
    name: str
    statements: list = field(default_factory=list)
    options: List[QuestionTypeOption] = field(default_factory=list)

@dataclass
class Template:
    id: str
    statements: List[str] = field(default_factory=list)
    question_types: Dict[str, QuestionType] = field(default_factory=dict)
    inherits: List[str] = field(default_factory=list)

@dataclass
class Topic:
    code: str
    name: str

    def label(self):
        return f"{self.code}: {self.name}"

@dataclass
class Course:
    name: str
    template: str
    topics: List[Topic] = field(default_factory=list)
    question_types: List[QuestionType] = field(default_factory=list)

@dataclass
class Subject:
    name: str
    courses: List[Course] = field(default_factory=list)

@dataclass
class Reflection:
    question_number: str = ""
    available_marks: int = 0
    achieved_marks: int = 0
    question_type: str = ""
    topics: List[Topic] = field(default_factory=list)
    selected_statements: list = field(default_factory=list)
    selected_options: dict = field(default_factory=dict)
    written_reflection: str = ""
    question_image: Image = None

    def marks_percentage(self):
        if self.available_marks > 0:
            marks_percentage = int((self.achieved_marks / self.available_marks) * 100)
        else:
            marks_percentage = 0
        return marks_percentage


@dataclass
class AssessmentReflection:
    student_name: str = ""
    assessment_name: str = ""
    subject: Subject = None
    course: Course = None
    reflections: List[Reflection] = field(default_factory=list)

    def generate_file_name(self, extension):
        file_name = ""
        if self.student_name:
            file_name += self.student_name
            if self.assessment_name:
                file_name += f" - {self.assessment_name}"
        elif self.assessment_name:
            file_name += f"{self.assessment_name}"
        file_name += f" reflection summary.{extension}"
        return file_name.strip()