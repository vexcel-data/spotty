#!/usr/bin/env python

from distutils.core import setup

setup(name='Cloud Training',
      version='1.0',
      description='Train models on AWS Spot Instances',
      author='Oleg Polosin',
      author_email='apls777@gmial.com',
      packages=['cloud_training', 'cloud_training.commands'],
      package_data={'cloud_training': ['data/launch-specification.json', 'data/unzip.py', 'data/user_data.sh']},
      scripts=['bin/cloud-training'])