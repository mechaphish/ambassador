#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ambassador log settings."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import logging
import os
import sys

DEFAULT_FORMAT = '%(asctime)s - %(name)-30s - %(levelname)-10s - %(message)s'

LOG = logging.getLogger('ambassador')
LOG.setLevel(os.environ.get('AMBASSADOR_LOG_LEVEL', 'DEBUG'))

HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(logging.Formatter(os.environ.get('AMBASSADOR_LOG_FORMAT', DEFAULT_FORMAT)))
LOG.addHandler(HANDLER)
