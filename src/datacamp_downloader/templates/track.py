from typing import List

from .course import Course


class Track:
    id: int
    title: str
    link: str
    courses: List[Course]

    def __init__(self, id: int, title: str, link: str) -> None:
        self.id = id
        self.title = title
        self.link = link
        self.courses = []
