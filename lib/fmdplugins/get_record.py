from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.cloud.dynamodb import DynamoDb, EncDynamoDb
from lib.exceptions.workflow import EntryException

@Action(GetStage.DATAGATHERING)
def get_record(context, output):
    output = []
    dynamodb = EncDynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key,
        context.configuration.master_pass)

    if not hasattr(context, 'fid'):
        raise EntryException('Attribute "fid" not provided')

    record = dynamodb.get(context.fid)
    context.basename = None
    if 'filename_history' in record:
        context.basename = record['filename_history'][0]['basename']
    return NamedEntity('record', record)
