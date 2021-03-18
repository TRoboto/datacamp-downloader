from dataclasses import dataclass, field
from typing import List


@dataclass
class Template:
    id: int
    name: str
    link: str


@dataclass
class Course(Template):
    pass


@dataclass
class Track(Template):
    courses: List[Course] = field(default_factory=list)