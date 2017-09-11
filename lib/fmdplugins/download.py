from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage
from lib.exceptions.workflow import EntryException, StageException
import tempfile

@Action(GetStage.RETRIEVING)
def download(context, data):
    s3storage = S3Storage(context.configuration.aws_default_region,
            context.configuration.aws_access_key_id,
            context.configuration.aws_secret_access_key)

    new_file, tempfilename = tempfile.mkstemp()
    context.filename = tempfilename
    s3storage.download(context.fid, context.filename)
    return context.filename
