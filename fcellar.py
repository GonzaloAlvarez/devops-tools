import click
import sys
from lib.fmd.filemetadata import FileMetadata, FileMetadataStore
from lib.fmd.workflow import FileManagementWorkflow
from lib.conf import Configuration
from lib.fmd.decorators import AddStage, ListStage, DelStage, GetStage
from lib.sys.cout import CLIHandler

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
            context.log.info('File [%s], mime [%s], id [%s]' % (entry['filename_history'][0]['src'], entry['mime'], entry['fid']))
            print entry['fid']

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
    print output

@click.command('del')
@click.argument('fid', type=click.STRING, required=True)
@click.pass_context
def _del(ctx, fid):
    context = ctx.obj
    context.fid = fid
    context.log.info('Removing entry with ID [%s]' % fid)
    fadm = FileManagementWorkflow()
    fadm.execute(context, DelStage)

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
