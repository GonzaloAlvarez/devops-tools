import os
from lib.encryption.aespcrypt import AESPCrypt
from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.file.tmpfile import TemporaryFile

@Action(AddStage.PROCESSING)
@DependsOn('compress')
def encrypt(context, output):
    new_file, encfilename = TemporaryFile.instance().new()
    aescrypt = AESPCrypt(context.configuration.master_pass)
    aescrypt.encrypt_file(context.filename, encfilename)
    context.filename=encfilename
    return NamedEntity('filename_history', [{
            'state': 'ENCRYPTED',
            'src': encfilename,
            'enc_algorithm': 'AES256'}])
    pass
