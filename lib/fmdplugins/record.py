from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.cloud.dynamodb import EncDynamoDb

@Action(AddStage.PROCESSING)
@DependsOn('store')
def record(context, data):
    dynamodb = EncDynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key,
        context.configuration.master_pass)
    dynamodb.put(data)
