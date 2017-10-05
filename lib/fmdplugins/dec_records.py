from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, DependsOn
from lib.fmd.tabledef import TableDefinition

@Action(ListStage.DATAGATHERING)
@DependsOn('list_records')
def dec_records(context, output):
    table_definition = TableDefinition(context.configuration)
    if 'records' in output:
        for entry in output['records']:
            for key, value in entry.iteritems():
                entry[key] = table_definition.decrypt_field(key, value)
