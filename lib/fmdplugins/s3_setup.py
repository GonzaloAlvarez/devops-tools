from lib.fmd.decorators import Action, AddStage, ListStage, GetStage, DelStage, ShowStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage

@Action(AddStage.SETUP, DelStage.SETUP, GetStage.SETUP, ListStage.SETUP, ShowStage.SETUP)
def s3_setup(context, data):
    if not hasattr(context, 's3'):
        context.s3 = S3Storage(context.configuration)
