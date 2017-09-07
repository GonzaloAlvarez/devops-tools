import os
from lib.fmd.decorators import Action,AddStage

@Action(AddStage.DATAGATHERING)
def size(context, output):
    return os.path.getsize(context.filename)
