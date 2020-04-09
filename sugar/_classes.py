#!/usr/bin/python3
"""
Server and Client
"""

import logging
import sys
import time
import threading
import concurrent.futures as con_futur

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

import paramiko
from paramiko.ssh_exception import SSHException


class Client:
    """
    Class representing client in terms of communication
    """
    def __init__(self, address, username="root", password=None):
        self._address = address
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self._ssh.connect(
            hostname=address, username=username, password=password)

    def __del__(self):
        logging.info("Closing connection to %s", self._address)
        self._ssh.close()

    def run_command(self, command):
        """
        Runs command on the Sugar client
        """
        _, out, err = self._ssh.exec_command(command)
        out, err = map(lambda f: f.read().decode(), (out, err))
        return out, err

    @property
    def address(self):
        """
        IP address of the client
        """
        return self._address


class Server:
    """
    Server class controlling clients
    """

    def serve(self):
        """
        Start to serve
        """
        self._server.serve_forever()

    def run(self, request):
        """
        /run
        """
        with self._rlock:
            command = request.POST['command']
            with con_futur.ThreadPoolExecutor(max_workers=self._workers) \
                    as executor:
                executor.map(lambda c: run_command(c, command),
                             self._clients.values())
            return Response('OK\r\n')

    def register(self, request):
        """
        /register
        """
        try:
            id_ = request.POST['id']
        except KeyError:
            response = Response('Missing id parameter')
            response.status_int = 400
            return response
        address = request.POST.get('address', request.client_addr)
        username = request.POST.get('username')
        if id_ in self._clients:
            if address != self._clients[id_].address:
                del self._clients[id_]
        else:
            try:
                self._clients[id_] = Client(address, username=username)
            except (SSHException, OSError) as error:
                logging.error(error)
                response = Response('SSH Error\r\n')
                response.status_int = 500
                return response
        return Response('OK %s\r\n' % request.POST['id'])

    def __init__(self, workers=8, port=9999):
        self._logging = logging.getLogger(__name__)
        self._clients = {}
        self._workers = workers
        self._rlock = threading.RLock()
        with Configurator() as config:
            config.add_route('register', '/register')
            config.add_route('run', '/run')
            config.add_view(self.run, route_name='run', request_method='POST')
            config.add_view(self.register, route_name='register',
                            request_method='POST')
            config.scan()
            app = config.make_wsgi_app()
        try:
            self._server = make_server('0.0.0.0', port, app)
        except OSError as error:
            self._logging.error(error)
            sys.exit(1)


def run_command(client, command):
    """
    Run command on a client and log stdout & stderr
    """
    out, err = client.run_command(command)
    with open("%s.txt" % client.address, "a") as file:
        print(">>> %s: %s:\nOUT:\n%s\nERR:\n%s\n" % (
            time.ctime(), client.address, out, err), file=file)
