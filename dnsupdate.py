"""
<<<<<<< HEAD
Usage: dnsupdate --ntfyfrom <ntfyfrom> --ntfyto <ntfyto>
       dnsupdate (-h | --help)

Options:
  --ntfyfrom    Email address to notify from
  --ntfyto      Email address to send notification to
=======
Usage: dnsupdate --ntfy <ntfy>
       dnsupdate (-h | --help)

Options:
  --ntfy        Email address to send notification
>>>>>>> d65979c73c4e21857eabef272fb820c619927301
  -h --help     Show this help

"""

import ipgetter, logging, yaml, smtplib, os, sys
from docopt import docopt
from lib.email import GMail
from lib.conf import Configuration
from lib.cloud import CloudFlare

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    arguments = docopt(__doc__, version='CloudFlare Manager 1.0')
    config = Configuration(__file__, 'config.yaml')
    config.addArguments(arguments)
    gmail = GMail(config.email_login, config.email_pass)
    cf = CloudFlare(config.cf_apiemail, config.cf_apikey)
    myip = ipgetter.myip()
    if cf.getCurrentIp(config.cf_host, config.cf_domain) == myip:
        logging.info('IP has not changed. Nothing to be done.')
    else:
        try:
            cf.updateDnsRecord(config.cf_domain, config.cf_host, ipgetter.myip())
<<<<<<< HEAD
            if hasattr(config, 'ntfyfrom') and hasattr(config, 'ntfyto'):
=======
            if hasattr(config, 'ntfy'):
>>>>>>> d65979c73c4e21857eabef272fb820c619927301
                email_content = "Greetings!\n\n"
                email_content += "    The IP for DNS Zone " + config.cf_host + '.' + config.cf_domain
                email_content += " has been updated to " + myip + ".\n\n"
                email_content += "Have a great day!"
<<<<<<< HEAD
                gmail.setFromAddress(config.ntfyfrom)
                from time import gmtime, strftime
                gmail.sendEmail(config.ntfyto,'IP Address has changed on ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()), email_content)
=======
                from time import gmtime, strftime
                gmail.sendEmail(config.ntfy,'IP Address has changed on ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()), email_content)
>>>>>>> d65979c73c4e21857eabef272fb820c619927301
        except:
            raise
