import logging
import tornado.ioloop
from apscheduler.schedulers.tornado import TornadoScheduler

from api.thirdparty import *


class PeriodicApplication(object):
    def __init__(self, Session):
        self.Session = Session

    def run(self):
        scheduler = TornadoScheduler()
        scheduler.add_job(sync_acba_sentence, "cron", hour='16', minute='43', args=[self.Session])
        scheduler.start()


