# Sugar > Salt

Sugar lets you run commands on registered clients.

## Python dependencies:

- paramiko
- pyramid

## Usage

1. On the server:

### Using the command line interface

`./sugar_server`

The server is running on the 9999 port by default.

Optional environment variables:
- `PORT`: Specify another port.
- `LOGGING`: Default logging level.  Must be `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- `WORKERS`: Maximum number of thread workers for the `/run` endpoint.  Default is 8.

### Using Sugar as a Python library

It is expected that Sugar is installed correctly in the Python library path on your machine.

```python
import sugar #Import the sugar module

sugar_server = sugar.Server(<WORKERS>, <PORT>) #Create a new sugar server object
sugar_server.serve() #Run the sugar server
```

```python
import sugar #Import the sugar module

sugar_client = Client(<ADDRESS>)
sugar_client.run_command(<COMMAND>)
```

2. On each client:

Make sure to install the server's SSH public key. This can be done from the server like this:

`ssh-copy-id root@client.fqdn`

To register the client with the server:

`curl -d "address=client.fqdn&id=$(</etc/machine-id)" server.fqdn:9999/register`

The machine-id is used to identify the client in case the IP address changes.

3. To run commands on all clients:

Example running `whoami`:

`curl -d "command=whoami" server.fqdn:9999/run`

The server will open SSH connections to each client and run the command.

On the same folder where `server.py` resides, you will find a `client.fqdn.txt` file with the logs containing a timestamp and stdout/stderr.

## POST parameters:

For the `/register` endpoint:

- `id`: The client's /etc/machine-id
- `address`: The client's address. This is optional. (This let us register a client from another machine).
- `username`: The client's username used by the server to connect via SSH to the client. This is optional. Defaults to `root`.

For the `/run` endpoint:

- `command`: The command to be run on all clients.

## TO DO:

- Add another POST parameter for the `/run` endpoint specifying a URL containing the script to be run.
- Docker image to have all dependencies packed with Python 3.
- Nginx for TLS (to be run alongside the Docker image for the app using Docker Compose).
- Fix bugs & introduce new ones.
- Add tests.
- Use CI for automatic testing.
- Embrace, extend, and extinguish: Replace Salt, Puppet, Chef & Ansible.