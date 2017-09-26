import os
from lib.fmd.decorators import Action, AddStage
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.DATAGATHERING)
def original_file(context, output):
    relname = context.filename
    for keypath in context.filetree:
        if context.filename.startswith(keypath['key']):
            relname = keypath['path'] + context.filename[len(keypath['key']):]
            break
    basename = os.path.basename(context.filename)
    dirname = os.path.dirname(context.filename)
    atime = int(os.path.getatime(context.filename))
    mtime = int(os.path.getmtime(context.filename))
    stat = os.lstat(context.filename)
    return NamedEntity('filename_history', [{
            'state': 'REGULAR',
            'src': context.filename,
            'relname': relname,
            'basename': basename,
            'dirname': dirname,
            'atime': atime,
            'mtime': mtime,
            'permissions': stat.st_mode}])
