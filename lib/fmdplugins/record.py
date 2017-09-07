from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.cloud.dynamodb import DynamoDb

@Action(AddStage.PROCESSING)
@DependsOn('store')
def record(context, data):
    dynamodb = DynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key)
    aescrypt = AESPCrypt(context.configuration.master_pass)
    dynamodb.put(aescrypt.encrypt_dict(data, ['fid', 'mime', 'size']))
