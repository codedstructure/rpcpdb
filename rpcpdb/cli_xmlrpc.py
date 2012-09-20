#!/usr/bin/env python -u

import xmlrpclib
from rpcpdb import cli


def get_api_connection():
    return xmlrpclib.ServerProxy('http://localhost:8000')
cli.get_api_connection = get_api_connection


if __name__ == '__main__':
    cli.main()
