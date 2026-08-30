class JobflowException(Exception): pass
class PlatformBlockedError(JobflowException): pass
class ParsingError(JobflowException): pass
class DatabaseError(JobflowException): pass
