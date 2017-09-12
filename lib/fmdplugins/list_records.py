from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.cloud.dynamodb import DynamoDb, EncDynamoDb
from lib.exceptions.workflow import EntryException

@Action(ListStage.DATAGATHERING)
def list_records(context, output):
    output = []
    dynamodb = EncDynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key,
        context.configuration.master_pass)

    if hasattr(context, 'filter'):
        context.log.debug('Using filter [%s]' % context.filter)
        entries = dynamodb.list(context.filter)
    else:
        entries = dynamodb.list()

    return NamedEntity('records', entries)
