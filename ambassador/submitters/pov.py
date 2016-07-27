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
        unprocessed = ExploitSubmissionCable.unprocessed()
        for cable in unprocessed.join(Exploit).where(Exploit.cs << fielded_cses):
            pov = cable.exploit
            LOG.info("Submitting POV %d for challenge %s", pov.id, pov.cs.name)
            try:
                result = self._cgc.uploadPOV(str(pov.cs.name),
                                             str(cable.team.name),
                                             str(cable.throws),
                                             str(pov.blob))
                LOG.debug("Submitted POV! Response: %s", result)
                submission_round, _ = Round.get_or_create(num=result['round'])
                pov.submit_to(team=cable.team, throws=cable.throws, round=submission_round)

            except TiError as err:
                LOG.error("POV Submission error: %s", err.message)

            cable.process()
