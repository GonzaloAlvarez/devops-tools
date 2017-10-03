import os
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity
from lib.exceptions.workflow import EntryException

@Action(AddStage.PRECONDITION)
@DependsOn('traverse')
def input_validation(context,  output):
    """Resolving symbolic links for files as inputs, and use the actual file moving forward
    """
    attrs = {}
    context.filename = os.path.abspath(context.filename)
    if not os.path.isfile(context.filename):
        raise EntryException('The file "%s" is not a valid regular file or it does not exists.' % context.filename)
    if os.path.islink(context.filename):
        attrs.update({'state':'LINK',
            'src': context.filename})
        context.filename = os.path.realpath(context.filename)
        return NamedEntity('filename_history', [attrs])

    return attrs
