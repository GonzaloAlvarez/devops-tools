from lib.fmd.decorators import DependsOn, Action, DelStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.dynamodb import DynamoDb

@Action(DelStage.PROCESSING)
@DependsOn('unlink')
def unregister(context, output):
    dynamodb = DynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key)

    dynamodb.remove(context.fid)
