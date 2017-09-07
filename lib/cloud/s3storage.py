import sys
import boto3
import hashlib

class S3Storage(object):
    def __init__(self, region, access_key, secret_key):
        self.s3 = boto3.resource(
                's3',
                region_name = region,
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key)
        self.bucket_name = hashlib.sha256(access_key + sys.argv[0]).digest().encode('hex')[0:30]
        if self.s3.Bucket(self.bucket_name) in self.s3.buckets.all():
            self.bucket = self.s3.Bucket(self.bucket_name)
        else:
            self.bucket = self.s3.create_bucket(Bucket = self.bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

    def store(self, filename, fid):
        with open(filename, 'rb') as in_file:
            s3obj = self.bucket.put_object(Key=fid, Body=in_file)
            s3obj.Acl().put(ACL='public-read')
            s3url = self.s3.meta.client.generate_presigned_url('get_object', Params = {'Bucket': self.bucket_name, 'Key': fid}, ExpiresIn = 0)
            return s3url
        return None

    def remove(self, fid):
        s3obj = self.s3.Object(self.bucket_name, fid)
        s3obj.delete()
        return None


