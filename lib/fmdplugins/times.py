import time
from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.DATAGATHERING)
@DependsOn('exif', 'original_file')
def times(context, data):
    itime = int(time.time())
    ctime = itime
    if 'filename_history' in data and len(data['filename_history']) > 0 and 'mtime' in data['filename_history'][0]:
        ctime = data['filename_history'][0]['mtime']
    if 'exif' in data and 'date' in data['exif']:
        ctime = data['exif']['date']

    return NamedEntity('time',{'itime': itime, 'ctime': ctime})
