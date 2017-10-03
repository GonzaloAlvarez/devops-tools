from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.encryption.aespcrypt import AESPCrypt

@Action(AddStage.PROCESSING)
@DependsOn('store', 'enc_record')
def record(context, data):
    context.ddb.put(data)
