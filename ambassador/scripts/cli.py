#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ambassador executable script"""

from __future__ import absolute_import

import os
import time

# leave this import before everything else!
import ambassador.settings

import ambassador.cgc.ticlient
import ambassador.cgc.tierror
import ambassador.log
from ambassador.notifier import Notifier
from ambassador.retrievers.status import StatusRetriever

LOG = ambassador.log.LOG.getChild('main')

class CLI(object):
    """A docstring"""
    POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))

    def __init__(self):
        """Another docstring"""
        # Initialize APIs
        self.cgc = ambassador.cgc.ticlient.TiClient.from_env()
        self.notifier = Notifier(tries_threshold=3)

    def run(self):
        """And another"""
        while True:
            try:
                # wait for API to be available
                while not self.cgc.ready():
                    self.notifier.api_is_down()
                    time.sleep(self.POLL_INTERVAL)

                self.notifier.api_is_up()

                status_retriever = StatusRetriever(self.cgc)
                status_retriever.run()

                LOG.info("Round #%d", status_retriever.current_round.num)

                # FeedbackRetriever(self.cgc, _round).run()
                # ConsensusEvaluationRetriever(self.cgc, _round).run()

            except ambassador.cgc.tierror.TiError:
                self.notifier.api_is_down()

        return 0


def main():
    """Oh shit"""
    CLI().run()
