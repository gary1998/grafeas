"""
Grafeas app on Bluemix
"""

# Always prefer setuptools over distutils
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='grafeas',
    version='1.0.0',
    description='IBM Grafeas: Cloud artifact metadata CRUD API and resource specifications',
    long_description=long_description,
    url='https://github.ibm.com/oneibmcloud/grafeas',
    license='IBM'
)
