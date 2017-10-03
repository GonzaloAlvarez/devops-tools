import os
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity
from lib.exceptions.workflow import EntryException, Severity

@Action(AddStage.DATAGATHERING)
@DependsOn('fid')
def duplicate(context, data):
    if data['fid'] in context.ddb.list_keys():
        exception = EntryException('Duplicate entry found in database')
        exception.severity = Severity.LOW
        raise exception
    
