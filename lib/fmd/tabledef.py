import json
from boto3.dynamodb.conditions import Key, Attr
from lib.encryption.aespcrypt import AESPCrypt

class TableDefinition(object):
    key = 'fid'
    filter_exprs = {
            'images': Attr('mime').begins_with('image'),
            'videos': Attr('mime').begins_with('video')
            }
    unencrypted_fields = ['fid', 'size', 'mime', 'time']

    def __init__(self, configuration):
        self.configuration = configuration
        self.aescrypt = AESPCrypt(configuration.master_pass)
        
    def encrypt_field(self, key, value):
        if key not in self.unencrypted_fields:
            return self.aescrypt.encrypt(json.dumps(value))
        return value

    def decrypt_field(self, key, value):
        if key not in self.unencrypted_fields:
            return json.loads(self.aescrypt.decrypt(value))
        return value
