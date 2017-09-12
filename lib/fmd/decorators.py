def DependsOn(*dependencies):
    def dependson_wrapper(function):
        function._dependencies = dependencies
        return function
    return dependson_wrapper

def Action(*stages):
    def action_wrapper(function):
        function._stages = stages
        return function
    return action_wrapper

class AddStage(object):
    PRECONDITION = 1
    DATAGATHERING = 2
    PROCESSING = 3


class ListStage(object):
    DATAGATHERING = 100
    PRESENTATION = 110


class DelStage(object):
    PROCESSING = 300


class GetStage(object):
    DATAGATHERING = 400
    RETRIEVING = 410
