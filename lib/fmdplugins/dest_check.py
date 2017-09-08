import os
from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.exceptions.workflow import EntryException

@Action(GetStage.DATAGATHERING)
def dest_check(context, output):
    if context.dest != None:
        absdest = os.path.abspath(context.dest)
        context.dest = os.path.realpath(context.dest)
        if not os.path.isdir(context.dest):
            raise EntryException('Destination path "%s" is not a folder' % context.dest)
        if not os.access('/path/to/folder', os.W_OK | os.X_OK):
            raise EntryException('Destination path "%s" is not writeable' % context.dest)
