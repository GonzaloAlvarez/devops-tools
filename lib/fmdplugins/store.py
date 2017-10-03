from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.PROCESSING)
@DependsOn('compress', 'encrypt')
def store(context, data):
    file_url = context.s3.store(context.filename,
            data['fid'])
    return NamedEntity('filename_history', [{
            'state': 'UPLOADED',
            'src': file_url,
            'store': 'S3'}])

