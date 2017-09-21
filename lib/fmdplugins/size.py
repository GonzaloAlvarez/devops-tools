import os
from lib.fmd.decorators import Action,AddStage
from lib.exceptions.workflow import EntryException, Severity

@Action(AddStage.DATAGATHERING)
def size(context, output):
    filesize = os.path.getsize(context.filename)
    if filesize != None and int(filesize) > 0:
        return filesize
    exception = EntryException('Empty file so not uploading')
    exception.severity = Severity.LOW
    raise exception
