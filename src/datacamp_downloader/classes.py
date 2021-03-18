from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Any
from .course import Course


@dataclass
class Track:
    id: int
    name: str
    link: str
    courses: List[Course] = field(default_factory=list)
