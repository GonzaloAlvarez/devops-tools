import os, yaml

class Configuration:
    def __init__(self, parentFile, configFileName):
        self.confFileName = os.path.join(os.path.dirname(os.path.realpath(parentFile)), configFileName)
        self.streamFile = open(self.confFileName, 'r')
        self.confDict = yaml.safe_load(self.streamFile)
        self.__dict__.update(self.confDict)


