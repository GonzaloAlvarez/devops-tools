import logging
import boto.ec2, boto.utils

class AWS:
    def __init__(self, apikey, apisecret, region='us-west-2'):
        self.ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=apikey, aws_secret_access_key=apisecret)

    def getInstances(self):
        reservations = self.ec2.get_all_instances()
        return [i for r in reservations for i in r.instances]

    def listInstances(self):
        for instance in self.getInstances():
            print(instance.id + ' - ' + instance.state)

    def startInstance(self, instanceId):
        for instance in self.getInstances():
            if instance.id == instanceId:
                instance.start()
                return True
        return False

    def stopInstance(self, instanceId):
        for instance in self.getInstances():
            if instance.id == instanceId:
                instance.stop()
                return True
        return False

    def getSelfInstanceId(self):
        try:
            oldLogLevel = logging.getLogger().getEffectiveLevel()
            logging.getLogger().setLevel(logging.CRITICAL)
            instanceId = boto.utils.get_instance_metadata(timeout=1, num_retries=2)['instance-id']
            logging.getLogger().setLevel(oldLogLevel)
            return instanceId
        except Exception as e:
            return None
