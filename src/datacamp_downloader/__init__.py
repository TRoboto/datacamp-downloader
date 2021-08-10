from colorama import init

from .session import Session

# use Colorama to make Termcolor work on Windows too
init()

active_session = Session()
datacamp = active_session.datacamp
