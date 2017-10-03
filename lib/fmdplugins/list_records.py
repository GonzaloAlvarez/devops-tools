from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.cloud.dynamodb import DynamoDb
from lib.exceptions.workflow import EntryException

@Action(ListStage.DATAGATHERING)
def list_records(context, output):
    output = []
    dynamodb = DynamoDb(context.configuration)

    if hasattr(context, 'filter'):
        context.log.debug('Using filter [%s]' % context.filter)
        entries = dynamodb.list(context.filter)
    else:
        entries = dynamodb.list()

    return NamedEntity('records', entries)
