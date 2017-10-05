from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.tabledef import TableDefinition

@Action(AddStage.PROCESSING)
@DependsOn('store')
def enc_record(context, data):
    table_definition = TableDefinition(context.configuration)
    for key, value in data.iteritems():
        data[key] = table_definition.encrypt_field(key, value)
