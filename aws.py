"""Usage: aws.py [options]
       aws.py [options] list
       aws.py [options] start <instance-id>
       aws.py [options] stop <instance-id>
       aws.py (-h | 00help)
       aws.py --version

Options:
  -d             Enable debug
  -h --help      Show this help
  --version      Show version

"""

import logging
from lib.conf import Configuration
from docopt import docopt
from lib.aws import AWS

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
