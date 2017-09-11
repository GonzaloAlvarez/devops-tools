import os
import gzip
import shutil

class Compressor(object):
    def __init__(self, zipfilename):
        self.zipfilename = zipfilename

    def compress(self, filename):
        with open(filename, 'rb') as f_in, gzip.open(self.zipfilename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            f_in.close()
            f_out.close()

    def deflate(self, output):
        with gzip.open(self.zipfilename, 'rb') as f_in, open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            f_in.close()
            f_out.close()

