from pyflare import PyflareClient
from lib.exceptions import RemoteOperationExecutionException, UnknownHostException

class CloudFlare:
    def __init__(self, api_email, api_key):
        self.cf = PyflareClient(api_email, api_key)

    def updateDnsRecord(self, domain, host, ip):
        try:
            cfHost = self.findHost(host, domain)
            if cfHost == None:
                raise UnknownHostException('The record must exist in order to call update')
            elif cfHost['content'] == ip:
                logging.info('IP has not changed')
            else:
                result = self.cf.rec_edit(domain, "A", cfHost['rec_id'], host, ip, 120, 0)
                cfUpdatedHost = self.findHost(host, domain)
                if cfUpdatedHost == None or cfUpdatedHost['content'] != ip:
                    logging.error('Unsuccessfully updated ip')
                    raise RemoteOperationExecutionException('CloudFlare API failed to update the API')
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


