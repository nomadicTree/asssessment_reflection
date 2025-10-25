from dataclasses import dataclass, field
from typing import List
from topic import Topic

@dataclass
class Course:
    name: str
    template: str
    topics: List[Topic] = field(default_factory=list)