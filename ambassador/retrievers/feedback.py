#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FeedbackRetriever module
"""

from __future__ import absolute_import

from farnsworth.models import (
    Feedback,
)

from ambassador.cgc.tierror import TiError
import ambassador.log
LOG = ambassador.log.LOG.getChild('feedback_retriever')


class FeedbackRetriever(object):
    """
    FeedbackRetriever class
    """

    def __init__(self, cgc, round_):
        """A normal __init__. Happy now pylint?"""
        self._cgc = cgc
        self._round = round_

    def _get_feedback(self, category):
        """Get feedback"""
        data = {}
        try:
            LOG.info("Getting {}".format(category))
            data = self._cgc.getFeedback(category, self._round.num)
        except TiError as e:
            LOG.warning("Feedback %s error: %s", category, e.message)
        return data

    def run(self):
        """A run() method. Happy now pylint?"""
        Feedback.update_or_create(self._round,
                                  polls=self._get_feedback('poll'),
                                  povs=self._get_feedback('pov'),
                                  cbs=self._get_feedback('cb'))
