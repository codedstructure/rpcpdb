#!/usr/bin/python

from distutils.core import setup

setup(
    name="rpcpdb",
    version="0.1",
    description="Debug support for RPC servers",
    long_description=open('README.txt').read(),
    author="Ben Bass",
    author_email="benbass@codedstructure.net",
    url="http://bitbucket.org/codedstructure/rpcpdb",
    packages=["rpcpdb"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development :: Debuggers",
    ]
)
