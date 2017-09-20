from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage

@Action(DelStage.PROCESSING)
def unlink(context, output):
    s3storage = S3Storage(context.configuration)

    s3storage.remove(context.fid)
    return None
