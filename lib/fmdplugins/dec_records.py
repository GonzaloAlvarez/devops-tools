import json
from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, DependsOn
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.tabledef import TableDefinition

@Action(ListStage.DATAGATHERING)
@DependsOn('list_records')
def dec_records(context, output):
    table_definition = TableDefinition()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    if 'records' in output:
        for entry in output['records']:
            for key, value in entry.iteritems():
                if key not in table_definition.unencrypted_fields:
                    entry[key] = json.loads(aescrypt.decrypt(value))
