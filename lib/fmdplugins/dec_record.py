from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ShowStage, GetStage, DependsOn
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.tabledef import TableDefinition

@Action(GetStage.DATAGATHERING, ShowStage.DATAGATHERING)
@DependsOn('get_record')
def dec_record(context, output):
    table_definition = TableDefinition(context.configuration)
    for key, value in output['record'].iteritems():
        output['record'][key] = table_definition.decrypt_field(key, value)
