from dataclasses import dataclass, field
from PIL import Image

@dataclass
class Reflection():
    question_number: str = ""
    available_marks: int = 0
    achieved_marks: int = 0
    question_type: str = ""
    topics: list = field(default_factory=list)
    selected_statements: list = field(default_factory=list)
    selected_option_statements: dict = field(default_factory=dict)
    written_reflection: str = ""
    question_image: Image = None
