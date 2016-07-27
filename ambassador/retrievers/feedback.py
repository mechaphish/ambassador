#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FeedbackRetriever module
"""

from __future__ import absolute_import

from farnsworth.models import (
    Feedback, ChallengeSet, ChallengeSetFielding, PollFeedback, Team
)

from ambassador.cgc.tierror import TiError
import ambassador.retrievers
LOG = ambassador.retrievers.LOG.getChild('feedback')


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
        cgc_polls = self._get_feedback('poll')
        Feedback.update_or_create(self._round,
                                  polls=cgc_polls,
                                  povs=self._get_feedback('pov'),
                                  cbs=self._get_feedback('cb'))

        fielded = {c.name: c for c in ChallengeSet.fielded_in_round(self._round)}
        for c in cgc_polls:
            cs = fielded[c['csid']]

            fielding = cs.fieldings.get((ChallengeSetFielding.available_round == self._round)
                                        & (ChallengeSetFielding.team == Team.get_our()))

            if fielding.poll_feedback is None:
                fnct, perf = c['functionality'], c['performance']
                pf = PollFeedback.create(cs=cs,
                                         round=self._round,
                                         success = float(fnct['success']) / 100.0,
                                         timeout = float(fnct['timeout']) / 100.0,
                                         connect = float(fnct['connect']) / 100.0,
                                         function = float(fnct['function']) / 100.0,
                                         time_overhead = float(perf['time']) / 100.0 - 1,
                                         memory_overhead = float(perf['memory']) / 100.0  - 1)
                fielding.poll_feedback = pf
                fielding.save()
