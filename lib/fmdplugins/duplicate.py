import os
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity
from lib.cloud.dynamodb import DynamoDb
from lib.exceptions.workflow import EntryException, Severity

@Action(AddStage.DATAGATHERING)
@DependsOn('fid')
def duplicate(context, data):
    dynamodb = DynamoDb(context.configuration.aws_default_region,
        context.configuration.aws_access_key_id,
        context.configuration.aws_secret_access_key)

    element = dynamodb.get(data['fid'])
    if element != None:
        exception = EntryException('Duplicate entry found in database')
        exception.severity = Severity.LOW
        raise exception
    
