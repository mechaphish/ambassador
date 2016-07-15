#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ambassador executable script"""

from __future__ import absolute_import

import os
import time

# leave this import before everything else!
import ambassador.settings

import ambassador.cgc.ticlient
import ambassador.log
from ambassador.notifier import Notifier
from ambassador.retrievers.status import StatusRetriever

LOG = ambassador.log.LOG.getChild('main')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 5))


def main():
    """Ambassador main body"""

    # Initialize APIs
    cgc = ambassador.cgc.ticlient.TiClient.from_env()
    notifier = Notifier()

    while True:
        try:
            # wait for API to be available
            while not cgc.ready():
                notifier.api_is_down()
                LOG.debug("Sleeping for %d seconds", POLL_INTERVAL)
                time.sleep(POLL_INTERVAL)

            notifier.api_is_up()

            status_retriever = StatusRetriever(cgc)
            status_retriever.run()

            LOG.info("Round #%d", status_retriever.current_round.num)

            # FeedbackRetriever(cgc, _round).run()
            # ConsensusEvaluationRetriever(cgc, _round).run()

        except ambassador.cgc.tierror.TiError:
            notifier.api_is_down()

    return 0
