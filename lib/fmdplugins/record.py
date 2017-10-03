from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.cloud.dynamodb import DynamoDb

@Action(AddStage.PROCESSING)
@DependsOn('store', 'enc_record')
def record(context, data):
    dynamodb = DynamoDb(context.configuration)
    dynamodb.put(data)
