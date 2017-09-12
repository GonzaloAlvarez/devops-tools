from lib.fmd.namedentity import NamedEntity
from lib.fmd.decorators import Action, ListStage, GetStage

@Action(ListStage.DATAGATHERING)
def print_record(context, data):
    if 'records' in data:
        for entry in data['records']:
            original_filename = entry['filename_history'][0]['basename']
            base_mime = entry['mime'].split('/')[0]
            if context.verbose > 0:
                rek_labels = ''
                if 'rekognition' in entry:
                    rek_labels = ','.join(entry['rekognition'])
                context.log.status('%s %s %s %s' % (entry['fid'], original_filename, base_mime, rek_labels))
            else:
                context.log.status('%s' % entry['fid'])
    else:
        context.log.status('Cellar does not contain any records matching your filter or it is empty')


