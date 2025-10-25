from dataclasses import dataclass, field
from PIL import Image

@dataclass
class Reflection:
    question_number: str = ""
    available_marks: int = 0
    achieved_marks: int = 0
    question_type: str = ""
    topics: list = field(default_factory=list)
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
