from dataclasses import dataclass, field
from typing import List
from .course import Course


@dataclass
class Track:
    id: int
    title: str
    link: str
    courses: List[Course] = field(default_factory=list)
