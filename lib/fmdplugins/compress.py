import tempfile
import zipfile
import os
from lib.fmd.decorators import DependsOn, Action, AddStage
from lib.fmd.namedentity import NamedEntity

class Compressor(object):
    def __init__(self, zipfilename):
        self.zipfilename = zipfilename
        self.zipfile = zipfile.ZipFile(self.zipfilename, 'w', zipfile.ZIP_DEFLATED)

    def compress(self, filename):
        self.zipfile.write(filename, os.path.basename(filename))

    def finish(self):
        self.zipfile.close()

@Action(AddStage.PROCESSING)
def compress(context, output):
    new_file, zipfilename = tempfile.mkstemp()
    compressor = Compressor(zipfilename)
    compressor.compress(context.filename)
    compressor.finish()
    context.filename=zipfilename
    return NamedEntity('filename_history', [{
            'state': 'COMPRESSED',
            'src': zipfilename,
            'zip_algorithm': 'ZIP'}])

