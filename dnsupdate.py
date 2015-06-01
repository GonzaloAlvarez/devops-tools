# Python DNS update for Cloud Flare

import ipgetter, logging, yaml, smtplib
from pyflare import PyflareClient

class SelfMailer:
    def __init__(self, conffile):
        stream = open(conffile, "r")
        self.config = yaml.load(stream)
        self.login = self.config["email_login"]
        self.password = self.config["email_pass"]
        if self.config.has_key("email_server"):
            self.smtpserver = self.config["email_server"]
        else:
            self.smtpserver = "smtp.gmail.com:587"
        self.toAddress = "Gonzalo Alvarez<gonzaloab@gmail.com>"
        self.fromAddress = "Newton Server<newton@gonzaloalvarez.es>"

    def mailme(self, subject, content):
        header  = 'From: %s\n' % self.fromAddress
        header += 'To: %s\n' % self.toAddress
        header += 'Subject: %s\n\n' % subject
        message = header + content

        server = smtplib.SMTP(self.smtpserver)
        server.starttls()
        server.login(self.login, self.password)
        result = server.sendmail(self.fromAddress, self.toAddress, message)
        server.quit()
        logging.info('Email sent successfully')
        return result

class DNSUpdater:
    def __init__(self, conffile):
        stream = open(conffile, "r")
        self.config = yaml.load(stream)
        self.cf = PyflareClient(self.config["cf_api_email"], self.config["cf_api_key"])
        self.email = SelfMailer(conffile)

    def trigger(self):
        logging.debug('Retrieving current IP')
        currentIp = ipgetter.myip()
        logging.info('Current IP: ' + currentIp)
        logging.debug('Retrieving cloudflare configuration')
        record = self.getHostRecord()
        if record == None:
            logging.error('Failed to find host ' + self.config["cf_dns_host"])
            return
        if record["content"] == currentIp:
            logging.info('IP has not changed')
        else:
            self.updateHostRecord(record["rec_id"], currentIp)
            updatedRecord = self.getHostRecord()
            if updatedRecord == None or updatedRecord["content"] != currentIp:
                logging.error('Something went wrong when updating the record')
            logging.info('IP Updated successfully')
            result = self.email.mailme('Newton Server IP Updated', 'Greetings,\n\nThe old IP was ' + record["content"] + ' and the new one is: ' + currentIp)

    def getHostRecord(self):
        records = self.cf.rec_load_all(self.config["cf_dns_zone"])
        found = False
        for record in records:
            if record["name"] == (self.config["cf_dns_host"] + "." + self.config["cf_dns_zone"]):
                found = True
                break
        if found:
            return record
        return None

    def updateHostRecord(self, recid, ip):
        try:
            result = self.cf.rec_edit(self.config["cf_dns_zone"], "A", recid, self.config["cf_dns_host"], ip, 120, 0)
        except:
            logging.error('Something failed while trying to update the register')
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dnsUpdater = DNSUpdater('config.yaml')
    dnsUpdater.trigger();

