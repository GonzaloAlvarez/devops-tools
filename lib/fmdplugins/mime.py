import magic,mimetypes
from lib.fmd.decorators import Action, AddStage

@Action(AddStage.DATAGATHERING)
def mime(context, output):
    mimeMagic = magic.Magic(mime=True)
    mimeType = mimeMagic.from_file(context.filename)
    return mimeType
 
