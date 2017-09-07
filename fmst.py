import click
import sys
from lib.fmd.filemetadata import FileMetadata, FileMetadataStore
from lib.fmd.workflow import FileManagementWorkflow
from lib.conf import Configuration
from lib.fmd.decorators import AddStage, ListStage, DelStage, GetStage

@click.command('add')
@click.argument('path', type=click.Path(file_okay=True), required=True)
@click.pass_context
def _add(ctx, path):
    context = ctx.obj
    context.filelist= [path]
    fadm = FileManagementWorkflow()
    fadm.execute_multiple(context, AddStage)

@click.command('list')
@click.pass_context
def _list(ctx):
    context = ctx.obj
    fadm = FileManagementWorkflow()
    output = fadm.execute(context, ListStage)
    if 'list_records' in output:
        for entry in output['list_records']:
            print entry['fid']

@click.command('get')
@click.argument('fid', type=click.STRING, required=True)
@click.pass_context
def _get(ctx, fid):
    context = ctx.obj
    context.fid = fid
    fadm = FileManagementWorkflow()
    output = fadm.execute(context, ListStage)
    print output

@click.command('del')
@click.argument('fid', type=click.STRING, required=True)
@click.pass_context
def _del(ctx, fid):
    context = ctx.obj
    context.fid = fid
    fadm = FileManagementWorkflow()
    fadm.execute(context, DelStage)

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj.debug = debug
    config = Configuration(sys.argv[0], 'config.yaml')
    ctx.obj.configuration = config

main.add_command(_add)
main.add_command(_get)
main.add_command(_del)
main.add_command(_list)

if __name__ =='__main__':
    main(obj=type('', (), {})())
