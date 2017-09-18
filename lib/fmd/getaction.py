import os
from lib.fmd.workflow import FileManagementWorkflow
from lib.fmd.decorators import GetStage, ListStage

class GetAction(object):
    def execute(self, context):
        fadm = FileManagementWorkflow()
        if context.fid == "all":
            context.log.status('Gathering list of files to download')
            record_list = fadm.execute(context, ListStage)
            context.fidlist = [record['fid'] for record in record_list['records']]
            context.log.status('Found %d entries to download' % len(context.fidlist))
            counter = 0
            for fid in context.fidlist:
                context.fid = fid
                counter += 1
                context.log.status('Processing fid [%s]' % os.path.basename(fid), counter , len(context.fidlist))
                fadm.execute(context, GetStage)
        else:
            output = fadm.execute(context, GetStage)
            context.log.status(context.filename)

