import click
import json
import yaml
import sys
import getpass
import os
from lib.conf import Configuration
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pykeepass import PyKeePass
from lib.encryption.aespcrypt import AESPCrypt

def init_keepass(ctx):
    keepass_filename = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.keepass_filename)
    gauth_settings_file = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.gauth_settings_filename)
    if not os.path.isfile(keepass_filename):
        gdrive_configuration = ctx.obj.configuration.gdrive_settings
        gdrive_configuration['save_credentials_file'] = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.gauth_credentials_filename)
        if not os.path.isfile(gauth_settings_file):
            print "From {}".format(ctx.obj.configuration.gdrive_secret_url)
            gdrive_configuration['client_config']['client_secret'] = getpass.getpass('Client Secret:')
            with open(gauth_settings_file, 'w') as settings_file:
                yaml.dump(gdrive_configuration, settings_file, default_flow_style=False)
        gauth = GoogleAuth(gauth_settings_file)
        gauth.CommandLineAuth()
        drive = GoogleDrive(gauth)
        password_file_list = drive.ListFile({'q': "title='%s'" % ctx.obj.configuration.keepass_filename}).GetList()
        password_file_obj = drive.CreateFile({'id': password_file_list[0]['id']})
        password_file_obj.GetContentFile(keepass_filename)
    with open(gauth_settings_file, 'r') as settings_file:
        settings_dict = yaml.load(settings_file)
        client_secret = settings_dict['client_config']['client_secret']
        aesclient = AESPCrypt(client_secret)
    password_key_file = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.password_key_filename)
    if not os.path.isfile(password_key_file):
        password_file_secret = getpass.getpass('KeePass Secret: ')
        encrypted_password_file_secret = aesclient.encrypt(password_file_secret)
        with open(password_key_file, 'w') as password_key_file_obj:
            password_key_file_obj.write(encrypted_password_file_secret)
    else:
        with open(password_key_file, 'r') as password_key_file_obj:
            encrypted_password_file_secret = password_key_file_obj.read()
        password_file_secret = aesclient.decrypt(encrypted_password_file_secret)
    return PyKeePass(keepass_filename, password=password_file_secret)


@click.command('clean')
@click.pass_context
def _clean(ctx):
    keepass_filename = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.keepass_filename)
    gauth_settings_file = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.gauth_settings_filename)
    gdrive_configuration_file = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.gauth_credentials_filename)
    password_key_file = os.path.join(ctx.obj.configuration.env.env_path, ctx.obj.configuration.password_key_filename)
    os.remove(keepass_filename)
    os.remove(gauth_settings_file)
    os.remove(gdrive_configuration_file)
    os.remove(password_key_file)


@click.command('init')
@click.pass_context
def _init(ctx):
    init_keepass(ctx)

@click.command('decode')
@click.argument('key', type=click.STRING, required=True)
@click.option('--format', '-f', 'formt', type=click.Choice(['yaml', 'shell']), default='yaml')
@click.pass_context
def _decode(ctx, key, formt):
    kp = init_keepass(ctx)
    entry = kp.find_entries(title=key, path='Applications/', first=True)
    if entry:
        attributes = {k:v for k,v in entry.custom_properties.items() if k != 'Notes'}
        if formt == 'yaml':
            print attributes
        elif formt == 'shell':
            for k,v in attributes.items():
                print 'export {}="{}"'.format(k.upper(), v.replace('\n','|'))

@click.group()
@click.option('-v', '--verbose', default=0, count=True)
@click.pass_context
def main(ctx, verbose):
    ctx.obj.verbose = verbose
    ctx.obj.configuration = Configuration(sys.argv[0], 'valkyrie.yml')

main.add_command(_decode)
main.add_command(_clean)
main.add_command(_init)

if __name__ =='__main__':
    main(obj=type('', (), {})())

