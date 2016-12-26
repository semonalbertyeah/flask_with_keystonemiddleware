# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

version = '0.1.0'
name='kapp'

setup(
    name=name,
    version=version,
    description='Flask with keystonemiddleware',
    long_description="Flask with keystonemiddleware'",
    packages=find_packages('.'),
    scripts=['kapp_manage'],
    zip_safe=False
)
