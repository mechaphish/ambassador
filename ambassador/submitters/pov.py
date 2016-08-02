#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POVSubmitter module
"""

from __future__ import absolute_import

from farnsworth.models import (ChallengeSet, Exploit, ExploitSubmissionCable, Round)

from ambassador.cgc.tierror import TiError
import ambassador.submitters
LOG = ambassador.submitters.LOG.getChild('pov')


class POVSubmitter(object):
    """
    POVSubmitter class
    """

    def __init__(self, cgc):
        """A docstring"""
        self._cgc = cgc

    def run(self):
        """Amazing docstring"""
        fielded_cses = ChallengeSet.fielded_in_round()
        most_recent = ExploitSubmissionCable.most_recent()
        for cable in most_recent.join(Exploit).where(Exploit.cs << fielded_cses):
            pov = cable.exploit
            LOG.info("Submitting POV %d for challenge %s", pov.id, pov.cs.name)
            try:
                result = self._cgc.uploadPOV(str(pov.cs.name),
                                             str(cable.team.name),
                                             str(cable.throws),
                                             str(pov.blob))
                LOG.debug("Submitted POV! Response: %s", result)

                submission_round, status = Round.get_or_create_latest(num=result['round'])

                if status == Round.FIRST_GAME:
                    LOG.error("Submission in first round of first game (round #%d)",
                                submission_round.num)
                elif status == Round.NEW_GAME:
                    LOG.info("Submission in first round of new game (round #%d)",
                                submission_round.num)
                elif status == Round.NEW_ROUND:
                    LOG.info("Submission beginning of new round #%d", submission_round.num)

                pov.submit_to(team=cable.team, throws=cable.throws, round=submission_round)

            except TiError as err:
                LOG.error("POV Submission error: %s", err.message)

            cable.process()
