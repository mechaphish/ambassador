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
    NOTIFY_AFTER_NUMBER_OF_TRIES = 3

    def __init__(self):
        """Another docstring"""
        # Initialize APIs
        self.cgc = ambassador.cgc.ticlient.TiClient.from_env()
        self.notifier = Notifier()
        self.api_down_tries = 0

    def api_is_down(self):
        """Another docstring again"""
        self.api_down_tries += 1
        if self.api_down_tries == self.NOTIFY_AFTER_NUMBER_OF_TRIES:
            self.notifier.api_is_down()

    def api_is_up(self):
        """And another"""
        self.api_down_tries = 0
        self.notifier.api_is_up()

    def run(self):
        """And another"""
        while True:
            try:
                # wait for API to be available
                while not self.cgc.ready():
                    self.api_down()
                    time.sleep(self.POLL_INTERVAL)

                self.api_up()

                status_retriever = StatusRetriever(self.cgc)
                status_retriever.run()

                LOG.info("Round #%d", status_retriever.current_round.num)

                # FeedbackRetriever(self.cgc, _round).run()
                # ConsensusEvaluationRetriever(self.cgc, _round).run()

            except ambassador.cgc.tierror.TiError:
                self.api_down()

        return 0


def main():
    """Oh shit"""
    CLI().run()
