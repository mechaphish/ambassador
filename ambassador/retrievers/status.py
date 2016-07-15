#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StatusRetriever module
"""

from __future__ import absolute_import, unicode_literals

from farnsworth.models import (
    Round,
    Score,
)

from ambassador.cgc.tierror import TiError
import ambassador.log
LOG = ambassador.log.LOG.getChild('status')


class StatusRetriever(object):
    """
    StatusRetriever module
    """

    def __init__(self, cgc):
        """A normal __init__. Happy now pylint?"""
        self._cgc = cgc
        self._round = None

    @property
    def current_round(self):
        return self._round

    def run(self):
        """A run() method. Happy now pylint?"""
        status = self._cgc.getStatus()
        self._round, _ = Round.get_or_create(num=status['round'])
        Score.update_or_create(self._round, scores=status['scores'])
