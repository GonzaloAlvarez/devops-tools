import tempfile
from lib.fmd.decorators import DependsOn, Action, GetStage
from lib.fmd.namedentity import NamedEntity
from lib.file.compression import Compressor

@Action(GetStage.RETRIEVING)
@DependsOn('decrypt')
def deflate(context, output):
    new_file, plainfilename = tempfile.mkstemp()
    compressor = Compressor(context.filename)
    compressor.deflate(plainfilename)
    context.filename = plainfilename
    return context.filename
