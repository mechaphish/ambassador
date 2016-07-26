#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ConsensusEvaluationRetriever module
"""

from __future__ import absolute_import

import os

from farnsworth.models import (
    ChallengeBinaryNode,
    ChallengeSet,
    ChallengeSetFielding,
    Evaluation,
    IDSRule,
    IDSRuleFielding,
    Team,
)

from ambassador.cgc.tierror import TiError
import ambassador.log
LOG = ambassador.log.LOG.getChild('retrievers.consensus_evaluation')


class ConsensusEvaluationRetriever(object):
    """
    ConsensusEvaluationRetriever class
    """

    def __init__(self, cgc, round_):
        self._cgc = cgc
        self._round = round_

    def _get_evaluation(self, category, team):
        """Get evaluation for cb and ids"""
        LOG.info("Getting %s consensus evaluation for team %s", category, team.name)
        data = []
        try:
            data = self._cgc.getEvaluation(category, self._round.num, team.name)
            for entry in data:
                if category == 'cb':
                    self._save_cs_fielding(entry, team)
                elif category == 'ids':
                    self._save_ids_fielding(entry, team)
        except TiError as e:
            LOG.warning("Consensus evaluation error: %s", e.message)
        return data

    def _save_cbn(self, cb_info, cs):
        tmp_path = os.path.join("/tmp", "{}-{}".format(cb_info['cbid'], cb_info['hash']))
        binary = self._cgc._get_dl(cb_info['uri'], tmp_path, cb_info['hash'])
        with open(tmp_path, 'rb') as fp:
            blob = fp.read()
        os.remove(tmp_path)
        cbn = ChallengeBinaryNode.create(name=cb_info['cbid'],
                                         cs=cs,
                                         blob=blob,
                                         sha256=cb_info['hash'])
        return cbn

    def _save_ids(self, ids_info, cs):
        tmp_path = os.path.join("/tmp", ids_info['hash'])
        ids_rule = self._cgc._get_dl(ids_info['uri'], tmp_path, ids_info['hash'])
        with open(tmp_path, 'rb') as fp:
            blob = fp.read()
        os.remove(tmp_path)
        ids = IDSRule.create(cs=cs, rules=blob, sha256=ids_info['hash'])
        return ids

    def _save_cs_fielding(self, cb_info, team):
        """Save CS fielding at current round for team"""
        cs, _ = ChallengeSet.get_or_create(name=cb_info['csid'])
        cs.seen_in_round(self._round)

        try:
            cbn = ChallengeBinaryNode.get((ChallengeBinaryNode.cs == cs) & \
                                          (ChallengeBinaryNode.name == cb_info['cbid']) & \
                                          (ChallengeBinaryNode.sha256 == cb_info['hash']))
        except ChallengeBinaryNode.DoesNotExist:
            cbn = self._save_cbn(cb_info, cs)
        try:
            csf = ChallengeSetFielding.get((ChallengeSetFielding.cs == cs) & \
                                           (ChallengeSetFielding.team == team) & \
                                           (ChallengeSetFielding.available_round == self._round))
            csf.add_cbns_if_missing(cbn)
        except ChallengeSetFielding.DoesNotExist:
            csf = ChallengeSetFielding.create(cs=cs, team=team,
                                              cbns=[cbn], available_round=self._round)

    def _save_ids_fielding(self, ids_info, team):
        """Save IDS fielding at current round for team"""
        cs, _ = ChallengeSet.get_or_create(name=ids_info['csid'])
        cs.seen_in_round(self._round)
        try:
            ids = IDSRule.get((IDSRule.sha256 == ids_info['hash']) & (IDSRule.cs == cs))
        except IDSRule.DoesNotExist:
            ids = self._save_ids(ids_info, cs)
        isf, _ = IDSRuleFielding.get_or_create(ids_rule=ids, team=team, available_round=self._round)

    def run(self):
        """Run! Run! Run!"""
        try:
            for team_id in self._cgc.getTeams():
                team, _ = Team.get_or_create(name=team_id)
                cbs = self._get_evaluation('cb', team)
                ids = self._get_evaluation('ids', team)
                Evaluation.update_or_create(self._round, team, cbs=cbs, ids=ids)
        except TiError as e:
            LOG.error("Unable to get teams: %s", e.message)
