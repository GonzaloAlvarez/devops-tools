import boto3
import hashlib

class BaseAws(object):
    DEFAULT_TAG = 'prod'
    def __init__(self, configuration):
        self.configuration = configuration
        self.region = configuration.aws_default_region
        self.access_key = configuration.aws_access_key_id
        self.secret_key = configuration.aws_secret_access_key
        self.tag = self.DEFAULT_TAG
        if hasattr(configuration, 'aws_tag'):
            self.tag = configuration.aws_tag
        if hasattr(configuration.env, 'aws_tag'):
            self.tag = configuration.env.aws_tag
        self.resource_name= hashlib.sha256(self.access_key + self.tag).digest().encode('hex')[0:32]

    def resource(self, service):
        return boto3.resource(
                service,
                region_name = self.region,
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key)

    def client(self, service):
        return boto3.client(
                service,
                region_name = self.region,
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key)

