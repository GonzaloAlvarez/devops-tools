import smtplib, yaml, logging

class GMail:
    """Send emails using a server, gmail by default"""
    def __init__(self, login, passwd, server="smtp.gmail.com:587"):
        self.login = login
        self.password = passwd
        self.smtpserver = server
        self.fromAddress = None

    def setFromAddress(self, fromAddress):
        self.fromAddress = fromAddress

    def sendEmail(self, toAddress, subject, content):
        header  = 'From: %s\n' % self.fromAddress
        header += 'To: %s\n' % toAddress
        header += 'Subject: %s\n\n' % subject
        message = header + content

        server = smtplib.SMTP(self.smtpserver)
        server.starttls()
        server.login(self.login, self.password)
        result = server.sendmail(self.fromAddress, toAddress, message)
        server.quit()
        logging.info('Email sent successfully')
        return result


