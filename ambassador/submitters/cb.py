#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CBSubmitter module
"""

from __future__ import absolute_import

import os
from farnsworth.models import (ChallengeSet, Round)

from ambassador.cgc.tierror import TiError
import ambassador.log
LOG = ambassador.log.LOG.getChild('submitters.cb')


class CBSubmitter(object):
    """
    CBSubmitter class
    """

    def __init__(self, cgc, current_round):
        """A docstring"""
        self._cgc = cgc
        self._current_round = current_round
        self._submit_rounds_interval = int(os.environ.get('SUBMIT_ROUNDS_INTERVAL', 3))

    def _submit_patches(self, cable):
        patches = [(str(cbn.root.name), str(cbn.blob))
                   for cbn in cable.cbns]
        result = self._cgc.uploadRCB(str(cable.cs.name), *patches)
        LOG.debug("Submitted RB! Response: %s", result)
        submission_round, _ = Round.get_or_create(num=result['round'])
        return cable.cs.submit(cbns=cable.cbns, round=submission_round)

    def _submit_ids_rule(self, cable):
        if cable.cbns and (cable.cbns[0].ids_rule is not None):
            ids_rule = cable.cbns[0].ids_rule
            result = self._cgc.uploadIDS(str(cable.cs.name), str(ids_rule.rules))
            submission_round, _ = Round.get_or_create(num=result['round'])
            return ids_rule.submit(round=submission_round)

    def run(self):
        """Amazing docstring"""
        # submit only in odd rounds, see FAQ163 & FAQ157
        # FIXME: Remove the following check for CFE
        if (self._current_round.num % self._submit_rounds_interval) == 1:
            for cs in ChallengeSet.fielded_in_round():
                # FIXME: Remove the following check for CFE
                if cs.has_submissions_in_round(self._current_round):
                    LOG.info("Skipping CS %s because has already a submission", cs.name)
                    continue

                for cable in cs.unprocessed_submission_cables():
                    try:
                        # FIXME: Possible race condition for patch and ids
                        # submission round
                        patches_fielding = self._submit_patches(cable)
                        ids_fielding = self._submit_ids_rule(cable)
                        cable.process()
                        if patches_fielding:
                            LOG.info("Submitted %d RBs for %s in round %d",
                                     patches_fielding.cbns.count(), cs.name,
                                     patches_fielding.submission_round.num)
                        if ids_fielding:
                            LOG.info("Submitted IDS for %s in round %d",
                                     cs.name, ids_fielding.submission_round.num)
                    except TiError as err:
                        LOG.error("RB Submission error: %s", err.message)

                    # one CS submission per round
                    break
