import os
from lib.fmd.decorators import Action, AddStage
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.PRECONDITION)
def traverse(context,  output):
    if os.path.isdir(context.filename):
        for dirName, subdirList, fileList in os.walk(context.filename):
            for filename in fileList:
                if not filename.startswith('.'):
                    context.filelist.append(os.path.join(dirName, filename))
        context.filetree.append({'key': context.filename, 'path': ''})
        context.filename = context.filelist.pop()

