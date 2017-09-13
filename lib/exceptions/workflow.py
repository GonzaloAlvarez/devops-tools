class Severity(object):
    LOW = 0
    HIGH = 2

class StageException(Exception):
    pass

class EntryException(Exception):
    severity = Severity.HIGH
    pass

class ExecutionException(Exception):
    pass
