from dataclasses import dataclass, field
from typing import List, Dict
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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
    selected_option_statements: dict = field(default_factory=dict)
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

    def create_summary_pdf(self, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("<b>Assessment Reflection</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"<b>Name:</b> {self.student_name}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Assessment:</b> {self.assessment_name}", styles["Normal"]))
        elements.append(Spacer(1, 18))

        elements.append(Paragraph(f"<b>Question Reflections</b>", styles["Heading2"]))

        for r in self.reflections:
            elements.append(Paragraph(f"<b>Question {r.question_number}</b>", styles["Heading3"]))
            marks_str = f"<b>Marks: </b> {r.achieved_marks}/{r.available_marks}"
            if r.marks_percentage():
                marks_str += f" ({r.marks_percentage()}%)"
            elements.append(Paragraph(marks_str, styles["Normal"]))
            elements.append(Paragraph(f"<b>Question type:</b> {r.question_type}"))
            topics_table_data = [["Topic code", "Topic name"]]
            for t in r.topics:
                topics_table_data.append([[t]])

            topics_table = Table(topics_table_data, colWidths=[80, 400])
            elements.append(topics_table)


        doc.build(elements)