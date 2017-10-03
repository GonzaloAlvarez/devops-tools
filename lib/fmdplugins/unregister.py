from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity

@Action(DelStage.PROCESSING)
@DependsOn('unlink')
def unregister(context, output):
    context.ddb.remove(context.fid)
