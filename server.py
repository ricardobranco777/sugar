#!/usr/bin/python3
"""
Server
"""

import logging
import sys
import time
import concurrent.futures

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


import paramiko
from paramiko.ssh_exception import SSHException

from utils import Singleton


PORT = 9999
CLIENTS = {}


@Singleton
class Client:
    """
    Client class
    """

    def __init__(self, hostname, username="root", password=None):
        self.hostname = hostname
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh.connect(hostname=hostname, username=username, password=password)

    def __del__(self):
        logging.info("Closing connection to %s\n", self.hostname)
        self.ssh.close()

    def run_command(self, command):
        """
        Runs command on the client
        """
        _, out, err = self.ssh.exec_command(command)
        out, err = map(lambda f: f.read().decode(), (out, err))
        return out, err


def run_command(client, command):
    """
    Run command on a client and log stdout & stderr
    """
    out, err = client.run_command(command)
    with open("%s.txt" % client.hostname, "a") as file:
        print(">>> %s: %s:\nOUT:%s\nERR:%s\n" % (
            time.ctime(), client.hostname, out, err), file=file)


@view_config(route_name='run', request_method='POST')
def run(request):
    """
    /run
    """
    command = request.POST['command']
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda client: run_command(client, command), CLIENTS.values())
    return Response('OK\r\n')


@view_config(route_name='register', request_method='POST')
def register(request):
    """
    /register
    """
    machine_id = request.POST['id']
    try:
        address = request.POST['address']
    except KeyError:
        address = request.client_addr
    try:
        username = request.POST['username']
    except KeyError:
        username = "root"
    if machine_id in CLIENTS and address != CLIENTS[machine_id].hostname:
        del CLIENTS[machine_id]
    try:
        client = Client(request.client_addr, username=username)
        CLIENTS[machine_id] = client
    except (SSHException, OSError) as error:
        logging.error(error)
        response = Response('SSH Error\r\n')
        response.status_int = 500
        return response
    return Response('OK %s\r\n' % request.POST['id'])


def main():
    """
    Main function
    """
    with Configurator() as config:
        config.add_route('register', '/register')
        config.add_route('run', '/run')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', PORT, app)
    server.serve_forever()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
