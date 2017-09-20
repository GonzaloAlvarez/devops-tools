import os
import traceback
import inspect
import pkgutil
import importlib
import time
from dag import DAG
from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import AddStage
from lib.exceptions.workflow import StageException, EntryException, Severity

class FileManagementWorkflow(object):
    def _build_world(self, stages):
        node_functions = {}
        stage_nodes = dict((k, []) for k in stages)
        for module_name in [name for _, name, _ in pkgutil.iter_modules(['lib/fmdplugins'])]:
            module = importlib.import_module('lib.fmdplugins.' + module_name)
            module_functions = [ (name, function) for name,function in inspect.getmembers(module, inspect.isfunction) if hasattr(function, '_stages')]
            for name, function in module_functions:
                for stage in function._stages:
                    if stage in stage_nodes:
                        stage_nodes[stage].append(name)
                node_functions.update({name: function})
        return node_functions, stage_nodes

    def _build_dag(self, stage_node_functions, node_functions):
            dag = DAG()
            for name, function in stage_node_functions.iteritems():
                dag.add_node(name)
            for name, function in stage_node_functions.iteritems():
                if hasattr(function,'_dependencies'):
                    for dependency in function._dependencies:
                        dag.add_edge(dependency, node_functions.keys()[node_functions.values().index(function)])
            return dag

    def _run_function(self, function, function_name, context, attrs):
        starttime = time.time()
        function_return = function(context, attrs)
        context.log.debug('Function [%s] took %d ms' % (function_name, round((time.time() - starttime) * 1000, 1)))
        if function_return:
            if type(function_return) is NamedEntity:
                if function_return.name in attrs and hasattr(attrs[function_return.name], '__iter__'):
                    attrs[function_return.name] = attrs[function_return.name] + function_return.data
                else:
                    attrs.update({function_return.name: function_return.data})
            else:
                attrs.update({function_name: function_return})

    def execute(self, context, stages_class = AddStage, override_functions=None):
        attrs = {}
        stages = sorted([value for name, value in vars(stages_class).iteritems() if not name.startswith('_')])
        node_functions, stage_nodes = self._build_world(stages)
        try:
            for stage in stages:
                dag = self._build_dag({name: node_functions[name] for name in stage_nodes[stage]}, node_functions)
                try:
                    context.log.debug('Graph: [%s]' % ','.join(dag.topological_sort()))
                    function_names = dag.topological_sort() if override_functions == None else override_functions
                    for function_name in function_names:
                        context.log.debug('Calling [%s] as part of stage [%s]' % (function_name, stage))
                        self._run_function(node_functions[function_name], function_name, context, attrs)
                except StageException as e:
                    context.log.info(str(e))
                    pass
        except EntryException as e:
            if e.severity == Severity.HIGH:
                context.log.error('Failed on phase [%s] with message [%s]' % (function_name, str(e)))
            else:
                context.log.info('Failed on phase [%s] with low severity message [%s]' %(function_name, str(e)))

        return attrs

