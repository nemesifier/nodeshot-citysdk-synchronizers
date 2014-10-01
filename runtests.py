#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os, sys
from django.core.management import execute_from_command_line


sys.path.append('%s/tests' % os.path.dirname(os.path.realpath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ci.settings")


if __name__ == "__main__":
    args = sys.argv
    args.append("test")
    args.append("nodeshot_citysdk_synchronizers")
    execute_from_command_line(args)
