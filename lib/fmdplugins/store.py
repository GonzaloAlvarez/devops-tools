from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.s3storage import S3Storage

@Action(AddStage.PROCESSING)
@DependsOn('compress', 'encrypt')
def store(context, data):
    s3storage = S3Storage(context.configuration)
    file_url = s3storage.store(context.filename,
            data['fid'])
    return NamedEntity('filename_history', [{
            'state': 'UPLOADED',
            'src': file_url,
            'store': 'S3'}])

