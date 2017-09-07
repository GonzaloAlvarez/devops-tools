from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.media import ExifTool

def get_exif(filename):
    with ExifTool() as et:
        return et.get_metadata(filename)

def lookup_exif_tags(exif_info, tags):
    for tag in tags:
        for prependTag in ('EXIF:', 'RIFF:'):
            lookupTag = prependTag + tag
            if lookupTag in exif_info:
                return exif_info[lookupTag]

def get_exif_key(key, exif_info, tags):
    data = lookup_exif_tags(exif_info, tags)
    if data != None:
        return {key:data}
    return {}

@Action(AddStage.DATAGATHERING)
@DependsOn('mime')
def exif(context, output):
    if output['mime'].startswith('image'):
        exif_info = get_exif(context.filename)
        return_tags = {}
        return_tags.update(get_exif_key('date', exif_info, ('DateTimeOriginal', 'DateTime', 'CreateDate', 'ModifyDate')))
        return_tags.update(get_exif_key('model', exif_info, ('Model',)))
        return_tags.update(get_exif_key('make', exif_info, ('Make',)))
        return_tags.update(get_exif_key('height', exif_info, ('ExifImageHeight',)))
        return_tags.update(get_exif_key('width', exif_info, ('ExifImageWidth',)))
        return return_tags
    if output['mime'].startswith('video'):
        exif_info = get_exif(context.filename)
        return_tags = {}
        return_tags.update(get_exif_key('codec', exif_info, ('VideoCodec',)))
        return_tags.update(get_exif_key('height', exif_info, ('ImageHeight',)))
        return_tags.update(get_exif_key('width', exif_info, ('ImageWidth',)))
        return_tags.update(get_exif_key('framerate', exif_info, ('FrameRate',)))
        return return_tags
    return None
