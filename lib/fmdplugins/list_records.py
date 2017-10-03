from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage
from lib.exceptions.workflow import EntryException

@Action(ListStage.DATAGATHERING)
def list_records(context, output):
    output = []

    if hasattr(context, 'filter'):
        context.log.debug('Using filter [%s]' % context.filter)
        entries = context.ddb.list(context.filter)
    else:
        entries = context.ddb.list()

    return NamedEntity('records', entries)
