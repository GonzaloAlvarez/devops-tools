from lib.fmd.decorators import Action, AddStage, ListStage, GetStage, DelStage, ShowStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.dynamodb import DynamoDb

@Action(AddStage.SETUP, DelStage.SETUP, GetStage.SETUP, ListStage.SETUP, ShowStage.SETUP)
def ddb_setup(context, data):
    if not hasattr(context, 'ddb'):
        context.ddb = DynamoDb(context.configuration)
