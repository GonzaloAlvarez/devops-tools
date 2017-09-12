import magic,mimetypes
from lib.fmd.decorators import Action, AddStage, DependsOn

@Action(AddStage.DATAGATHERING)
@DependsOn('duplicate')
def mime(context, output):
    mimeMagic = magic.Magic(mime=True)
    mimeType = mimeMagic.from_file(context.filename)
    return mimeType
 
