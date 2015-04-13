#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    content = file.read()

setup(
    name='aiodocker',
    version='0.1',
    description='Docker wrapper for asyncio',
    long_description=content,
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    url='https://github.com/johnnoone/aioconsul',
    packages=[
        'aiodocker'
    ],
    keywords=[
        'infrastructure',
        'asyncio',
        'container'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Clustering',
    ],
    install_requires=[
        'aiohttp>=0.15.1',
        'python-dateutil>=2.4'
    ],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    }
)
