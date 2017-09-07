import os
from lib.fmd.decorators import Action, AddStage
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.DATAGATHERING)
def original_file(context, output):
    basename = os.path.basename(context.filename)
    dirname = os.path.dirname(context.filename)
    atime = os.path.getatime(context.filename)
    mtime = os.path.getmtime(context.filename)
    stat = os.lstat(context.filename)
    return NamedEntity('filename_history', [{
            'state': 'REGULAR',
            'src': context.filename,
            'basename': basename,
            'dirname': dirname,
            'atime': atime,
            'mtime': mtime,
            'permissions': stat.st_mode}])
