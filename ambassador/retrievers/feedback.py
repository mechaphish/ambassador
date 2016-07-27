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


        currently_fielded = { c.name: c for c in ChallengeSet.fielded_in_round(self._round) }
        for c in cgc_polls:
            cs = currently_fielded[c['csid']]

            fielding = cs.fieldings.where(
                ChallengeSetFielding.available_round == self._round,
                ChallengeSetFielding.team == Team.get_our()
            ).get()

            if fielding.poll_feedback is not None:
                continue

            pf = PollFeedback.create(
                cs=cs,
                round_id=self._round.id,
                success = float(c['functionality']['success'])/100.,
                timeout = float(c['functionality']['timeout'])/100.,
                connect = float(c['functionality']['connect'])/100.,
                function = float(c['functionality']['function'])/100.,
                time_overhead = float(c['performance']['time'])/100. - 1.,
                memory_overhead = float(c['performance']['memory'])/100. - 1.,
            )
            fielding.poll_feedback = pf
            fielding.save()
