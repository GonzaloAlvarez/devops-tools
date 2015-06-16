import logging
from boto3.session import Session

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


