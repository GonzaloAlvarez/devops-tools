import json
from lib.fmd.workflow import FileManagementWorkflow
from lib.fmd.decorators import ShowStage

class ShowAction(object):
    def execute(self, context):
        fadm = FileManagementWorkflow()
        output = fadm.execute(context, ShowStage)
        context.log.status(json.dumps(output['record'], sort_keys=True, indent=4))

