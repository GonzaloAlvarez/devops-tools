from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.dynamodb import DynamoDb

@Action(DelStage.PROCESSING)
@DependsOn('unlink')
def unregister(context, output):
    dynamodb = DynamoDb(context.configuration)

    dynamodb.remove(context.fid)
