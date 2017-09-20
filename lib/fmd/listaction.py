from lib.fmd.workflow import FileManagementWorkflow
from lib.fmd.decorators import ListStage

class ListAction(object):
    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def execute(self, context):
        fadm = FileManagementWorkflow()
        data = fadm.execute(context, ListStage)
        totalsize = 0
        if 'records' in data and len(data['records']) > 0:
            for entry in data['records']:
                original_filename = entry['filename_history'][0]['basename']
                base_mime = entry['mime'].split('/')[0]
                totalsize += int(entry['size'])
                if context.verbose > 0:
                    rek_labels = ''
                    if 'rekognition' in entry:
                        rek_labels = ','.join(entry['rekognition'])
                    context.log.status('%s %s %s %s' % (entry['fid'], original_filename, base_mime, rek_labels))
                else:
                    context.log.status('%s' % entry['fid'])
            if context.verbose > 0:
                context.log.status('Summary:')
                context.log.status(' - Count of files: %d' % len(data['records']))
                context.log.status(' - Size of files: %s ' % ListAction.sizeof_fmt(totalsize))
        else:
            context.log.status('Cellar does not contain any records matching your filter or it is empty')

