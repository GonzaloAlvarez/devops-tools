from lib.file import hashfile
from lib.fmd.decorators import Action,AddStage

@Action(AddStage.DATAGATHERING)
def fid(context, output):
    return hashfile.sha256(context.filename)

