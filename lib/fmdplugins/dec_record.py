import json
from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ShowStage, GetStage, DependsOn
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.tabledef import TableDefinition

@Action(GetStage.DATAGATHERING, ShowStage.DATAGATHERING)
@DependsOn('get_record')
def dec_record(context, output):
    table_definition = TableDefinition()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    for key, value in output['record'].iteritems():
        if key not in table_definition.unencrypted_fields:
            output['record'][key] = json.loads(aescrypt.decrypt(value))
