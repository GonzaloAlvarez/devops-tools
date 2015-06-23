"""Usage: aws [options]
       aws [options] list
       aws [options] start <instance-id>
       aws [options] stop <instance-id>
       aws [options] instanceid
       aws (-h | --help)
       aws --version

Options:
  -d             Enable debug
  -h --help      Show this help
  --version      Show version

"""

import logging
from lib.conf import Configuration
from docopt import docopt
from lib.cloud import AWS

if __name__ == '__main__':
    arguments = docopt(__doc__, version='AWS Manager 1.0')
    config = Configuration(__file__, 'config.yaml')
    if arguments['-d']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)
    logging.info(arguments)
    aws = AWS(config.aws_apikey, config.aws_apisecret)
    if arguments['list'] == True:
        aws.listInstances()
    elif arguments['instanceid'] == True:
        instanceId = aws.getSelfInstanceId()
        if instanceId == None:
            print('This is not an AWS instance')
        else:
            print(instanceId)
    elif arguments['start'] == True:
        aws.startInstance(arguments['<instance-id>'])
    elif arguments['stop'] == True:
        aws.stopInstance(arguments['<instance-id>'])
