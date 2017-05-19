#!/usr/bin/env python
import codecs
import re
from os import path

from setuptools import find_packages, setup


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-polymorphic',
    version=find_version('polymorphic', '__init__.py'),
    license='BSD',

    description='Seamless Polymorphic Inheritance for Django Models',
    long_description=read('README.rst'),
    url='https://github.com/django-polymorphic/django-polymorphic',

    author='Bert Constantin',
    author_email='bert.constantin@gmx.de',

    maintainer='Christopher Glass',
    maintainer_email='tribaal@gmail.com',

    packages=find_packages(),
    include_package_data=True,

    test_suite='runtests',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
