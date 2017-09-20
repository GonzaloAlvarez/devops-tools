import sys
from lib.cloud.baseaws import BaseAws

class S3Storage(BaseAws):
    def __init__(self, configuration):
        super(S3Storage, self).__init__(configuration)
        self.s3 = self.resource('s3')
        self.bucket_name = self.resource_name
        if self.s3.Bucket(self.bucket_name) in self.s3.buckets.all():
            self.bucket = self.s3.Bucket(self.bucket_name)
        else:
            self.bucket = self.s3.create_bucket(Bucket = self.bucket_name, CreateBucketConfiguration={'LocationConstraint': self.region})

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

    def download(self, fid, filename):
        self.bucket.download_file(fid, filename)
