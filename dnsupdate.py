# Python DNS update for Cloud Flare

import ipgetter, logging, yaml, smtplib, os
from pyflare import PyflareClient
from lib.email import GMail
from lib.conf import Configuration

class RemoteOperationFailedException(Exception):
    pass

class UnknownHostRecordException(Exception):
    pass

class CloudFlare:
    def __init__(self, api_email, api_key):
        self.cf = PyflareClient(api_email, api_key)

    def updateDnsRecord(self, domain, host, ip):
        try:
            cfHost = self.findHost(host, domain)
            if cfHost == None:
                raise UnknownHostRecordException('The record must exist in order to call update')
            elif cfHost['content'] == ip:
                logging.info('IP has not changed')
            else:
                result = self.cf.rec_edit(domain, "A", cfHost['rec_id'], host, ip, 120, 0)
                cfUpdatedHost = self.findHost(host, domain)
                if cfUpdatedHost == None or cfUpdatedHost['content'] != ip:
                    logging.error('Unsuccessfully updated ip')
                    raise RemoteOperationFailedException('CloudFlare API failed to update the API')
        except:
            logging.error('Something failed while trying to update the register')
            raise
        return 200

    def findHost(self, host, domain):
        records = self.cf.rec_load_all(domain)
        for record in records:
            if record["name"] == (host + "." + domain):
                return record
        return None

    def getCurrentIp(self, host, domain):
        record = self.findHost(host, domain)
        return record['content'] if record != None else None

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
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
