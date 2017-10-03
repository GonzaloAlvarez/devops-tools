import json
from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.tabledef import TableDefinition

@Action(AddStage.PROCESSING)
@DependsOn('store')
def enc_record(context, data):
    table_definition = TableDefinition()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    for key, value in data.iteritems():
        if key not in table_definition.unencrypted_fields:
            data[key] = aescrypt.encrypt(json.dumps(value))
