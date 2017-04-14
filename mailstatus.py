import jinja2
import subprocess
from urllib2 import urlopen
from json import load
import subprocess, os
import requests
from lib.conf import Configuration
import datetime

if __name__ =='__main__':
    self_path = os.path.dirname(os.path.realpath(__file__))
    loader = jinja2.FileSystemLoader(self_path + '/status')
    env = jinja2.Environment(loader=loader)
    template = env.get_template('email-template.html')
    commands=[]
    timenow = datetime.datetime.now().strftime("%c")
    my_env = os.environ.copy()
    my_env["PATH"] = self_path + ":" + my_env["PATH"]
    with open(self_path + '/status/commands') as f:
        for line in f:
            p = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=my_env)
            command_output = ''.join(str(x) for x in p.stdout.readlines())
            command_output = ''.join([i if ord(i) < 128 else ' ' for i in command_output])
            commands.append({'line':'# ' + line,'output':command_output})
    host={'ip': load(urlopen('https://api.ipify.org/?format=json'))['ip']}
    output = template.render(commands=commands, host=host)
    config = {}
    if os.path.exists(os.path.join(self_path, 'config.yaml')):
        config = Configuration(__file__, 'config.yaml')
    elif os.path.exists(os.path.join(self_path, 'mail.yaml')):
        config = Configuration(__file__, 'mail.yaml')
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(config.mailgun_domain)
    request = requests.post(request_url, auth=('api', config.mailgun_apikey), data={
        'from': 'Server Status <' + config.email_login + '>',
        'to': config.email_recipient,
        'subject': '[' + host['ip'] + '] Status on ' + timenow,
        'html': output
        })
    with open('/tmp/my_new_html_file.html', 'w') as f:
         f.write(output)
