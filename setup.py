#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys
from nodeshot_citysdk_synchronizers import get_version


name = 'nodeshot-citysdk-synchronizers'
package = 'nodeshot_citysdk_synchronizers'
description = 'Additional synchronizers for nodeshot.interop.sync'
url = 'http://github.com/nemesisdesign/nodeshot-citysdk-synchronizers/'
author = 'Federico Capoano'
author_email = 'f[dot]capoano[at]cineca[dot]it'
license = 'BSD'
install_requires = ['nodeshot']


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload --sign")
    args = {'version': get_version()}
    print "You probably want to also tag the version now:"
    print "  git tag -s %(version)s" % args
    print "  git push --tags"
    sys.exit()


setup(
    name=name,
    version=get_version(),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires
)
