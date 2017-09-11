import os
import tempfile
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.exceptions.workflow import EntryException, StageException

@Action(GetStage.RETRIEVING)
@DependsOn('deflate')
def settle(context, output):
    if not context.dest:
        raise StageException('File "%s" not downloaded' % context.fid)
    if not context.basename:
        raise EntryException('Original filename not properly stored. File "%s" not downloaded' % context.fid)
    destfile = os.path.join(context.dest, context.basename)
    if os.path.isfile(destfile):
        raise EntryException('File "%s" already exists in destination. Skipping.' % destfile)
    if not os.path.isfile(context.filename):
        raise EntryException('Something went wrong with the downloaded file "%s"' % context.filename)
    
    os.rename(context.filename, destfile)

    context.filename = destfile
    return context.filename
