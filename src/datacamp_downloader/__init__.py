from .session import Session
import copyreg
import ssl

session = Session.load()
datacamp = session.datacamp
# handle ssl saving issues
copyreg.pickle(ssl.SSLContext, lambda obj: (obj.__class__, (obj.protocol,)))