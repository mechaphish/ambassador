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

import ambassador.retrievers
LOG = ambassador.retrievers.LOG.getChild('status')


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

    def run(self):
        """
        Update game status, including round number and the current scores.

        If we notice that the round number has jumped backward, explicitly create a new round.
        """
        LOG.debug("Getting status")
        status = self._cgc.getStatus()
        self._round, round_status = Round.get_or_create_latest(num=status['round'])

        if round_status == Round.FIRST_GAME:
            LOG.info("First game starts")
        elif round_status == Round.NEW_GAME:
            LOG.info("New game started")
        elif round_status == Round.NEW_ROUND:
            LOG.info("New round started")
        elif round_status == Round.SAME_ROUND:
            LOG.debug("Continuing current round")

        Score.update_or_create(self._round, scores=status['scores'])
