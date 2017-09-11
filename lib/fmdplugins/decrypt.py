import os
import tempfile
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity

@Action(GetStage.RETRIEVING)
@DependsOn('download')
def decrypt(context, output):
    new_file, decfilename = tempfile.mkstemp()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    aescrypt.decrypt_file(context.filename, decfilename)
    context.filename = decfilename
    return context.filename
