from boto3.dynamodb.conditions import Key, Attr

class TableDefinition(object):
    key = 'fid'
    filter_exprs = {
            'images': Attr('mime').begins_with('image'),
            'videos': Attr('mime').begins_with('video')
            }
    unencrypted_fields = ['fid', 'size', 'mime']
