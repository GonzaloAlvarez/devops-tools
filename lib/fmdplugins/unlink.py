from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity

@Action(DelStage.PROCESSING)
def unlink(context, output):
    context.s3.remove(context.fid)
    return None
