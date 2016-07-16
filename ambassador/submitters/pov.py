#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
POVSubmitter module
"""

from __future__ import absolute_import

from farnsworth.models import (ExploitSubmissionCable, Round)

from ambassador.cgc.tierror import TiError
import ambassador.log
LOG = ambassador.log.LOG.getChild('submitters.pov')


class POVSubmitter(object):
    """
    POVSubmitter class
    """

    def __init__(self, cgc):
        """A docstring"""
        self._cgc = cgc

    def run(self):
        """Amazing docstring"""
        for cable in ExploitSubmissionCable.unprocessed():
            pov = cable.exploit
            try:
                result = self._cgc.uploadPOV(str(pov.cs.name),
                                             str(cable.team.name),
                                             str(cable.throws),
                                             str(pov.blob))
                LOG.debug("Submitted POV! Response: %s", result)
                submission_round = Round.get(Round.num == result['round'])
                pov.submit_to(team=cable.team, throws=cable.throws, round=submission_round)

            except TiError as err:
                LOG.error("POV Submission error: %s", err.message)

            cable.process()
