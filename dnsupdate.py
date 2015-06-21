"""
Usage: cloudflare.py 
       cloudflare.py (-h | --help)

Options:
  -h --help     Show this help

"""

import ipgetter, logging, yaml, smtplib, os
from docopt import docopt
from lib.email import GMail
from lib.conf import Configuration
from lib.cloud import CloudFlare

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    arguments = docopt(__doc__, version='CloudFlare Manager 1.0')
    config = Configuration(__file__, 'config.yaml')
    gmail = GMail(config.email_login, config.email_pass)
    cf = CloudFlare(config.cf_apiemail, config.cf_apikey)
    myip = ipgetter.myip()
    if cf.getCurrentIp(config.cf_host, config.cf_domain) == myip:
        logging.info('IP has not changed. Nothing to be done.')
    else:
        try:
            cf.updateDnsRecord(config.cf_domain, config.cf_host, ipgetter.myip())
            email_content = "Greetings!\n\n"
            email_content += "    The IP for DNS Zone " + config.cf_host + '.' + config.cf_domain
            email_content += " has been updated to " + myip + ".\n\n"
            email_content += "Have a great day!"
            gmail.setFromAddress('newton@gonzaloalvarez.es')
            gmail.sendEmail('gonzaloab@gmail.com','IP Address has changed', email_content)
        except:
            raise
