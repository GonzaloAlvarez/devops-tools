import json
from lib.fmd.workflow import FileManagementWorkflow
from lib.fmd.decorators import ShowStage

class ShowAction(object):
    def execute(self, context):
        fadm = FileManagementWorkflow()
        output = fadm.execute(context, ShowStage)
        if 'record'in output:
            context.log.status(json.dumps(output['record'], sort_keys=True, indent=4))
        else:
            context.log.status('We have found no file in the database with id [%s]' % context.fid)
