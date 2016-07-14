#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ambassador executable script"""

import ambassador.log

LOG = ambassador.log.LOG.getChild('main')

def main():
    LOG.info("ciao")
