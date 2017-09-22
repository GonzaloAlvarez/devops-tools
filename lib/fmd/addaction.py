import os
from lib.fmd.workflow import FileManagementWorkflow
from lib.fmd.decorators import AddStage
from lib.file.tmpfile import TemporaryFile

class AddAction(object):
    def execute(self, context):
        counter = 0
        fadm = FileManagementWorkflow()
        for filename in context.filelist:
            context.filename = filename
            counter += 1
            context.log.status('Processing file [%s]' % os.path.basename(filename), counter , len(context.filelist))
            fadm.execute(context, AddStage)
            TemporaryFile.instance().cleanup()
        context.log.finish()

