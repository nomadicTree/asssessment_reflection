from dataclasses import dataclass, field
from typing import List
from course import Course

@dataclass
class Subject:
    name: str
    courses: List[Course] = field(default_factory=list)