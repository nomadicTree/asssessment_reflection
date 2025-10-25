from dataclasses import dataclass, field
from typing import List
from subject import Subject
from course import Course
from reflection import Reflection

@dataclass
class AssessmentReflection:
    student_name: str = ""
    assessment_name: str = ""
    subject: Subject = None
    course: Course = None
    reflections: List[Reflection] = field(default_factory=list)