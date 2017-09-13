import click
import sys
from lib.fmd.workflow import FileManagementWorkflow
from lib.conf import Configuration
from lib.fmd.decorators import AddStage, ListStage, DelStage, GetStage
from lib.fmd.actions import AddAction
from lib.sys.cout import CLIHandler
from lib.fmd.tabledef import TableDefinition

@click.command('add')
@click.argument('path', type=click.Path(dir_okay=True, file_okay=True), required=True, nargs=-1)
@click.pass_context
def _add(ctx, path):
    context = ctx.obj
    context.filelist= [path_entry.rstrip('/') for path_entry in path]
    AddAction().execute(context)

@click.command('list')
@click.option('--filter', 'flt', type=click.Choice(TableDefinition.filter_exprs.keys()))
@click.pass_context
def _list(ctx, flt):
    context = ctx.obj
    context.filter = flt
    fadm = FileManagementWorkflow()
    output = fadm.execute(context, ListStage)

@click.command('get')
@click.argument('fid', type=click.STRING, required=True)
@click.option('--dest', type=click.Path(exists=True), required=False)
@click.pass_context
def _get(ctx, fid, dest):
    context = ctx.obj
    context.fid = fid
    context.dest = dest
    fadm = FileManagementWorkflow()
    output = fadm.execute(context, GetStage)
    context.log.info(str(output))
    context.log.status(context.filename)

@click.command('del')
@click.argument('fid', type=click.STRING, required=True)
@click.pass_context
def _del(ctx, fid):
    context = ctx.obj
    context.fid = fid
    context.log.info('Removing entry with ID [%s]' % fid)
    fadm = FileManagementWorkflow()
    fadm.execute(context, DelStage)
    context.log.status('File [%s] removed' % fid)

@click.group()
@click.option('-v', '--verbose', default=0, count=True)
@click.pass_context
def main(ctx, verbose):
    ctx.obj.verbose = verbose
    config = Configuration(sys.argv[0], 'config.yaml')
    ctx.obj.configuration = config
    CLIHandler(ctx.obj)

main.add_command(_add)
main.add_command(_get)
main.add_command(_del)
main.add_command(_list)

if __name__ =='__main__':
    main(obj=type('', (), {})())
