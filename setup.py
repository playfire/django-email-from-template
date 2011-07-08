#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-email-from-template',
    description="Send emails generated entirely from Django templates.",
    version='0.1',
    url='http://code.playfire.com/',

    author='Playfire.com',
    author_email='tech@playfire.com',
    license='BSD',

    packages=find_packages(),
    package_data={'': [
        'templates/*/*',
    ]},
)
