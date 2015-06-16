"""Usage: aws.py [-d]
          aws.py [-d] list
          aws.py [-d] start <instance-id>
          aws.py stop <instance-id>
          aws.py status <instance-id>
          aws.py (-h | 00help)
          aws.py --version

Options:
  -d             Enable debug
  -h --help      Show this help
  --version      Show version

"""

import logging
from boto3.session import Session
from lib.conf import Configuration
from docopt import docopt

class AWS:
    def __init__(self, apikey, apisecret, region='us-west-2'):
        self.session = Session(aws_access_key_id=apikey, aws_secret_access_key=apisecret, region_name=region)
        self.ec2 = self.session.resource('ec2')

    def listInstances(self):
        for instance in self.ec2.instances.all():
            print(instance.id + ' - ' + instance.state['Name'])

    def startInstance(self, instanceId):
        found = False
        for instance in self.ec2.instances.all():
            if instance.id == instanceId:
                found = True
                instance.start()
                print('Instance has been started')
        if not found:
            print('Instance [' + instanceId + '] was not found')

    def stopInstance(self, instanceId):
        found = False
        for instance in self.ec2.instances.all():
            if instance.id == instanceId:
                found = True
                instance.stop()
                print('Instance has been stopped')
        if not found:
            print('Instance [' + instanceId + '] was not found')

if __name__ == '__main__':
    arguments = docopt(__doc__, version='AWS Manager 1.0')
    config = Configuration(__file__, 'config.yaml')
    if arguments['-d']:
        logging.basicConfig(level=logging.INFO)
    logging.info(arguments)
    aws = AWS(config.aws_apikey, config.aws_apisecret)
    if arguments['list'] == True:
        aws.listInstances()
    elif arguments['start'] == True:
        aws.startInstance(arguments['<instance-id>'])
    elif arguments['stop'] == True:
        aws.stopInstance(arguments['<instance-id>'])
