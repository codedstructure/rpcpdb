#!/usr/bin/python

from distutils.core import setup

setup(
    name="rpc_pdb",
    version="0.1",
    description="Debug support for RPC servers",
    author="Ben Bass",
    author_email="benbass@codedstructure.net",
    url="http://bitbucket.org/codedstructure/rpc_pdb",
    packages=["rpc_pdb"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development :: Debuggers",
    ]
)
