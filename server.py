#!/usr/bin/python3

import logging
import sys

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


import paramiko
from paramiko.ssh_exception import SSHException

from utils import Singleton


PORT = 9999
USERNAME = "ricardo"
SCRIPT = "ls /"
CLIENTS = {}


@Singleton
class Client:
    def __init__(self, hostname, username="root", password=None):
        self.hostname = hostname
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh.connect(hostname=hostname, username=username, password=password)

    def __del__(self):
        logging.info("Closing connection to %s\n" % self.hostname)
        self.ssh.close()

    def run_command(self, command):
        _, out, err = self.ssh.exec_command(command)
        out, err = map(lambda f: f.read().decode(), (out, err))
        return out, err


@view_config(route_name='register', request_method='POST')
def handle_client(request):
    machine_id = request.POST['id']
    if machine_id in CLIENTS and request.client_addr != CLIENTS[machine_id].hostname:
        del CLIENTS[machine_id]
    try:
        client = Client(request.client_addr, username=USERNAME)
        CLIENTS[machine_id] = client
    except (SSHException, OSError) as error:
        logging.error(error)
        response = Response('SSH Error\r\n')
        response.status_int = 500
        return response
    #print(id(hash))
    out, err = client.run_command(SCRIPT)
    with open("%s.txt" % client.hostname, "a") as file:
        print("%s:\nOUT:%s\nERR:%s\n" % (client.hostname, out, err), file=file)
    return Response('OK %s\r\n' % request.POST['id'])


def main():
    with Configurator() as config:
        config.add_route('register', '/')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', PORT, app)
    server.serve_forever()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
