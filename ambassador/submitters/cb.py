#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CBSubmitter module
"""

from __future__ import absolute_import

from farnsworth.models import (ChallengeSetSubmissionCable,
                               ChallengeSetFielding,
                               IDSRuleFielding, Round, Team)

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

    def run(self):
        """Amazing docstring"""
        # submit only in odd rounds, see FAQ163 & FAQ157
        if (self._current_round.num % 2) == 1:

          for cable in ChallengeSetSubmissionCable.unprocessed():
              patch = cable.cbns
              original_cbid = patch.root.name
              # FIXME!!!!
              fixme = ChallengeSetFielding.select().where((ChallengeSetFielding.cs == cable.cbns.cs) & \
                                                          (ChallengeSetFielding.submission_round == self._current_round) & \
                                                          (ChallengeSetFielding.team == Team.get_our()))
              if len(fixme) > 0:
                  LOG.info("patch for CS already submitted in this round, move on...")
                  break

              try:
                  # submit rb
                  result = self._cgc.uploadRCB(str(cable.cs.name),
                                               (str(original_cbid),
                                                str(patch.blob)))
                  LOG.debug("Submitted RB! Response: %s", result)
                  submission_round, _ = Round.get_or_create(num=result['round'])
                  cable.cs.submit_patches(submission_round, patch)
                  # submit ids
                  if patch.ids_rule is not None:
                      result = self._cgc.uploadIDS(str(cable.cs.name), str(patch.ids_rule.rules))
                      submission_round, _ = Round.get_or_create(num=result['round'])
                      IDSRuleFielding.get_or_create(ids_rule=patch.ids_rule,
                                                    submission_round=submission_round,
                                                    team=Team.get_our())

              except TiError as err:
                  LOG.error("RB Submission error: %s", err.message)

              cable.process()
