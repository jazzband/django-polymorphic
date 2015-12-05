#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name = 'django_polymorphic',
    license = 'BSD',

    description = 'Seamless Polymorphic Inheritance for Django Models',
    long_description = read('README.rst'),
    url = 'https://github.com/chrisglass/django_polymorphic',

    author = 'Bert Constantin',
    author_email = 'bert.constantin@gmx.de',

    maintainer = 'Christopher Glass',
    maintainer_email = 'tribaal@gmail.com',

    packages = find_packages(),
    package_data = {
        'polymorphic': [
            'templates/admin/polymorphic/*.html',
        ],
    },

    test_suite='runtests',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    use_scm_version={
        'version_scheme': 'post-release',
        'write_to': 'polymorphic/version.py',
    },
    setup_requires=['setuptools_scm'],
)
