#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CBSubmitter module
"""

from __future__ import absolute_import

from datetime import datetime, timedelta
import os

from farnsworth.models import (ChallengeSet, Round)

from ambassador.cgc.tierror import TiError
import ambassador.submitters
LOG = ambassador.submitters.LOG.getChild('cb')

MAX_ROUND_AGE = 240


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

    @property
    def _safe_to_submit(self):
        submission_deadline = self._round.created_at + timedelta(seconds=MAX_ROUND_AGE)
        return datetime.now() > submission_deadline

    def run(self):
        to_act_on, to_ignore = set(), set()
        cables = self._current_round.cs_submission_cables \
                                    .order_by(CSSubmissionCable.created_at.desc())

        # For each cable, check if we want to act on it:
        # We go through all cables from most recent to least recent.
        # We only act on cables:
        # - If it was not processed in the past.
        # - There does not exist a more recent cable for the same CS
        #   (otherwise we should ignore it and process the one).
        for cable in cables:
            if cable.processed_at is None and cable.cs not in to_ignore:
                to_act_on.append(cable)
            else:
                to_ignore.append(cable.cs)

        LOG.info("%d cables to act on, ignoring %d cables", len(to_act_on), len(to_ignore))

        # Process all cables we want to act on
        while to_act_on and self._safe_to_submit:
            cable = to_act_on.pop()
            try:
                # Possible race condition for patch and ids submission
                # round that is alleviated by our safe_to_submit check
                patches_fielding = self._submit_patches(cable)
                ids_fielding = self._submit_ids_rule(cable)
                cable.process()
                if patches_fielding:
                    LOG.info("Submitted %d RBs for %s in round %d", patches_fielding.cbns.count(),
                             cs.name, patches_fielding.submission_round.num)
                if ids_fielding:
                    LOG.info("Submitted IDS for %s in round %d", cs.name,
                             ids_fielding.submission_round.num)
            except TiError as err:
                LOG.error("RB Submission error: %s", err.message)

        if to_act_on:
            LOG.info("Missed out to act on %d cables", len(to_act_on))
        else:
            LOG.info("Submitted all I had to submit")
