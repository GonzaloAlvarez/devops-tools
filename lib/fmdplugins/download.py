from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage
from lib.exceptions.workflow import EntryException, StageException
from lib.file.tmpfile import TemporaryFile

@Action(GetStage.RETRIEVING)
def download(context, data):
    s3storage = S3Storage(context.configuration)

    new_file, tempfilename = TemporaryFile.instance().new()
    context.filename = tempfilename
    s3storage.download(context.fid, context.filename)
    return context.filename
