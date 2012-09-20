#!/usr/bin/env python -u

import Pyro.core
from rpcpdb import cli


def get_api_connection():
    return Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")
cli.get_api_connection = get_api_connection


if __name__ == '__main__':
    cli.main()
