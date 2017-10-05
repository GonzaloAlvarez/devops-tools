from lib.fmd.decorators import DependsOn, Action, AddStage

@Action(AddStage.DATAGATHERING)
@DependsOn('mime', 'size')
def rekognition(context, data):
    if data['mime'].startswith('image') and int(data['size']) < 5 * 1024 * 1024:
        try:
            with open(context.filename, 'rb') as image:
                result = context.rekognition.detect_labels(
                        Image = {'Bytes': image.read()},
                        MinConfidence = 85.0)
            labels = [label['Name'] for label in result['Labels']]
            return labels
        except Exception as e:
            context.log.debug('Rekognition failed for image [%s] with message %s' % (context.filename, str(e)))
    return None
