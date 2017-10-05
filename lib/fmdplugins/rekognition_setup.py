from lib.fmd.decorators import Action, AddStage
from lib.fmd.namedentity import NamedEntity
from lib.cloud.baseaws import BaseAws

@Action(AddStage.SETUP)
def rekognition_setup(context, data):
    if not hasattr(context, 'rekognition'):
        aws = BaseAws(context.configuration)
        context.rekognition = aws.client('rekognition')
