import os

from setuptools import setup, find_packages

import sqlify

try:
    with open(os.path.abspath('./README.rst')) as stream:
        long_description = stream.read()
except:
    long_description = 'A simple sql builder based on standard Python type hints'

setup(
    name="sqlify",
    version=sqlify.VERSION,
    packages=find_packages(),
    extras_require = {
        'postgresql':  ["psycopg2-binary"]
    },
    classifiers=['Topic :: Database',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'Development Status :: 3 - Alpha'],
    author='Gabriel',
    description='A simple sql builder based on standard Python type hints',
    long_description=long_description,
    license='BSD',
    keywords='psycopg2 postgresql sqlite sqlite3 sql database',
    url='https://github.com/G4brym/sqlify',
)
