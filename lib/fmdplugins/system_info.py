import socket
import os
import pwd
import platform
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity

@Action(AddStage.DATAGATHERING)
@DependsOn('original_file')
def sysinfo(context, data):
    fqdn = socket.getfqdn()
    hostname = socket.gethostname()
    mountpath = context.filename
    uname = os.uname()
    platform_data = str(platform.platform())
    pid = os.getpid()
    username = pwd.getpwuid(os.getuid()).pw_name
    while not os.path.ismount(mountpath):
        mountpath = os.path.dirname(mountpath)
    return NamedEntity('sysinfo', {
        'fqdn': fqdn,
        'hostname': hostname,
        'uname': uname,
        'platform': platform_data,
        'pid': pid,
        'user': username,
        'mountpath': mountpath
        })
