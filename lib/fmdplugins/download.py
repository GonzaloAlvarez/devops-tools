from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.exceptions.workflow import EntryException, StageException
from lib.file.tmpfile import TemporaryFile

@Action(GetStage.RETRIEVING)
def download(context, data):
    new_file, tempfilename = TemporaryFile.instance().new()
    context.filename = tempfilename
    context.s3.download(context.fid, context.filename)
    return context.filename
