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
    SETUP = 1
    PRECONDITION = 2
    DATAGATHERING = 3
    PROCESSING = 4


class ListStage(object):
    SETUP = 100
    DATAGATHERING = 110
    PRESENTATION = 120


class DelStage(object):
    SETUP = 300
    PROCESSING = 310


class GetStage(object):
    SETUP = 400
    DATAGATHERING = 410
    RETRIEVING = 420

class ShowStage(object):
    SETUP = 500
    DATAGATHERING = 510
