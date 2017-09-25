import socket
import os
import pwd
import sys
import platform
from lib.fmd.decorators import Action, AddStage, DependsOn
from lib.fmd.namedentity import NamedEntity
from lib.cloud.baseaws import BaseAws

@Action(AddStage.DATAGATHERING)
@DependsOn('original_file')
def sysinfo(context, data):
    baseaws = BaseAws(context.configuration)
    fqdn = socket.getfqdn()
    hostname = socket.gethostname()
    mountpath = context.filename
    homepath = os.path.expanduser("~")
    currdir = os.getcwd()
    uname = os.uname()
    platform_data = str(platform.platform())
    invocation = sys.argv
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
        'homepath': homepath,
        'currdir': currdir,
        'aws_access_id': baseaws.access_key,
        'aws_tag': baseaws.tag,
        'aws_resource_id': baseaws.resource_name,
        'invocation': invocation,
        'mountpath': mountpath
        })
