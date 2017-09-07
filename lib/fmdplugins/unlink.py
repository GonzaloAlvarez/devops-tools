from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage

@Action(DelStage.PROCESSING)
def unlink(context, output):
    s3storage = S3Storage(context.configuration.aws_default_region,
            context.configuration.aws_access_key_id,
            context.configuration.aws_secret_access_key)

    s3storage.remove(context.fid)
    return None
