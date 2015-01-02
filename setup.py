import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='rage',
    version='0.1.0',
    packages=['rage'],
    url='https://github.com/tmr232/rage',
    license='MIT',
    author='Tamir Bahar',
    author_email='',
    description='Windows Registry Manipulation',
    long_description=(read('README.rst')),
)
