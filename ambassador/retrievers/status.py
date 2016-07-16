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

import ambassador.log
LOG = ambassador.log.LOG.getChild('retrievers.status')


class StatusRetriever(object):
    """
    StatusRetriever class
    """

    def __init__(self, cgc):
        """A normal __init__. Happy now pylint?"""
        self._cgc = cgc
        self._round = None

    @property
    def current_round(self):
        """Return corrent round"""
        return self._round

    def _save_round(self, status):
        """Save current round"""
        self._round, _ = Round.get_or_create(num=status['round'])

    def _save_scores(self, status):
        """Save scores"""
        Score.update_or_create(self._round, scores=status['scores'])

    def run(self):
        """A run() method. Happy now pylint?"""
        LOG.info("Getting status")
        status = self._cgc.getStatus()
        self._save_round(status)
        self._save_scores(status)
