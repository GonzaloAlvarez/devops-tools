from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.cloud.dynamodb import DynamoDb

@Action(ListStage.DATAGATHERING, GetStage.DATAGATHERING)
def list_records(context, output):
    output = []
    dynamodb = DynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key)

    aescrypt = AESPCrypt(context.configuration.master_pass)
    if hasattr(context, 'fid'):
        return aescrypt.decrypt_dict(dynamodb.get(context.fid), ['fid', 'mime', 'size'])
    else:
        entries = dynamodb.list()
        for entry in entries:
            output.insert(len(output), aescrypt.decrypt_dict(entry, ['fid', 'mime', 'size']))
        return output
