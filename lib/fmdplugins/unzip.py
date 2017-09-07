import os
import tempfile
import zipfile
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.DATAGATHERING)
@DependsOn('mime')
def unzip(context,  output):
    if output['mime'] == 'application/zip':
        tempdir = tempfile.mkdtemp()
        with zipfile.ZipFile(context.filename) as zf:
            zf.extractall(tempdir)
        context.filelist.append(tempdir)
