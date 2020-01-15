#!/usr/bin/python3

import logging
import sys

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import paramiko
from paramiko.ssh_exception import SSHException

from utils import Singleton


PORT = 9999
USERNAME = "ricardo"
SCRIPT = "ls /"
CLIENTS = set()


@Singleton
class Client:
    def __init__(self, hostname, password=None):
        self.hostname = hostname
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.connect(hostname=hostname, username=USERNAME, password=password)

    def run_command(self, command):
        _, out, err = self.ssh.exec_command(command)
        out, err = map(lambda f: f.read().decode(), (out, err))
        return out, err


def handle_client(request):
    try:
        client = Client(request.client_addr)
    except (SSHException, OSError) as error:
        logging.error(error)
        response = Response('ERROR')
        response.status_int = 500
        return response
    CLIENTS.add(client)
    out, err = client.run_command(SCRIPT)
    with open("%s.txt" % client.hostname, "a") as file:
        print("%s:\nOUT:%s\nERR:%s\n" % (client.hostname, out, err), file=file)
    return Response('OK')


def main():
    with Configurator() as config:
        config.add_route('register', '/')
        config.add_view(handle_client, route_name='register')
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', PORT, app)
    server.serve_forever()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)