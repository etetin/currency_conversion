import argparse
import os
import sys

from .src.server import Server


try:
    app_id = os.environ['APP_ID']
except KeyError:
    sys.exit('Variable APP_ID is not setted. exit')


parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--port')
args = parser.parse_args()

custom_server_params = {}
# TODO may be validation for passed arguments?
if args.host is not None:
    custom_server_params['host'] = args.host

if args.port is not None:
    custom_server_params['port'] = int(args.port)

server = Server(**custom_server_params)

server.run()
