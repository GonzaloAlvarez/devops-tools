from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.file.compression import Compressor
from lib.file.tmpfile import TemporaryFile

@Action(AddStage.PROCESSING)
def compress(context, output):
    new_file, zipfilename = TemporaryFile.instance().new()
    compressor = Compressor(zipfilename)
    compressor.compress(context.filename)
    context.filename=zipfilename
    return NamedEntity('filename_history', [{
            'state': 'COMPRESSED',
            'src': zipfilename,
            'zip_algorithm': 'ZIP'}])

