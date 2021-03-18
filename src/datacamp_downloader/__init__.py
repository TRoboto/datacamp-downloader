from .session import Session
import copyreg
import ssl

active_session = Session.load()
datacamp = active_session.datacamp
# handle ssl saving issues
copyreg.pickle(ssl.SSLContext, lambda obj: (obj.__class__, (obj.protocol,)))