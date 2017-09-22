import os
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.file.tmpfile import TemporaryFile

@Action(GetStage.RETRIEVING)
@DependsOn('download')
def decrypt(context, output):
    new_file, decfilename = TemporaryFile.instance().new()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    aescrypt.decrypt_file(context.filename, decfilename)
    context.filename = decfilename
    return context.filename
