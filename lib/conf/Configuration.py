import os, yaml

class Configuration:
    def __init__(self, parentFile, configFileName):
        self.confFileName = os.path.join(os.path.dirname(os.path.realpath(parentFile)), configFileName)
        with open(self.confFileName, 'r') as streamFile:
            confDict = yaml.safe_load(streamFile)
            self.__dict__.update(confDict)
        self.env = type('', (), {})()
        self.env.__dict__.update({key.lower(): os.environ[key] for key in os.environ})

    def addArguments(self, arguments):
        for key in arguments:
            if key.startswith('--') and '<' + key[2:] + '>' in arguments:
                pass
            if key.startswith('<') and key.endswith('>'):
                self.__dict__[key[1:][:-1]] = arguments[key]
