import xxhash
import mmap
from lib.file import hashfile
from lib.fmd.decorators import Action,AddStage

@Action(AddStage.DATAGATHERING)
def fid(context, output):
    BLOCKSIZE = 1024 ** 2
    readdigest = xxhash.xxh64()
    with open(context.filename, 'rb') as in_file:
        for item in iter((lambda: in_file.read(BLOCKSIZE)), ''):
            readdigest.update(item)
    return readdigest.hexdigest()

