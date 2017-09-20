from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ShowStage, GetStage
from lib.cloud.dynamodb import DynamoDb, EncDynamoDb
from lib.exceptions.workflow import EntryException

@Action(GetStage.DATAGATHERING, ShowStage.DATAGATHERING)
def get_record(context, output):
    output = []
    dynamodb = EncDynamoDb(context.configuration)

    if not hasattr(context, 'fid'):
        raise EntryException('Attribute "fid" not provided')

    record = dynamodb.get(context.fid)
    if record == None:
        raise EntryException('File with fid [%s] not found in the database' % context.fid)
    return NamedEntity('record', record)
