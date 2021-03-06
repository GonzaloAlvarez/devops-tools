from logging.handlers import SysLogHandler, RotatingFileHandler
import tempfile
import logging
import sys
import os
from progress.bar import ChargingBar

class CursorVisibleChargingBar(ChargingBar):
    hide_cursor = False

class CLIHandler(object):
    LEVELS = [logging.WARN, logging.INFO, logging.DEBUG, logging.DEBUG]

    def __init__(self, context):
        self.verbose = context.verbose
        self.pbtotal = 0
        if sys.platform == 'darwin':
            address = '/var/run/syslog'
        else:
            address = '/dev/log'
        tempfile_handle, self.tempfile = tempfile.mkstemp(prefix=os.path.basename(sys.argv[0]))
        file_logger = RotatingFileHandler(self.tempfile, mode='a', maxBytes=5*1024*1024,
                                          backupCount=2, encoding=None, delay=0)
        file_logger_formatter = logging.Formatter('%(asctime)s %(name)s.%(module)s.%(funcName)s: [%(levelname)s] %(message)s')
        file_logger.setFormatter(file_logger_formatter)
        file_logger.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_logger)
        logging.getLogger().setLevel(logging.DEBUG)

        console_logger = logging.StreamHandler()
        console_logger.setLevel(CLIHandler.LEVELS[self.verbose])
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s - |%(name)s.%(module)s|')
        console_logger.setFormatter(console_formatter)
        main_logger = 'main' if self.verbose < 3 else ''
        logging.getLogger(main_logger).addHandler(console_logger)
        logging.getLogger(main_logger).setLevel(CLIHandler.LEVELS[self.verbose])
        logging.getLogger(main_logger).info('Initializing logs. Full debug log can be found at [%s]' % self.tempfile)

        self.log = context.log = type('', (), {})()
        context.log.info = logging.getLogger(main_logger).info
        context.log.error = logging.getLogger(main_logger).error
        context.log.debug = logging.getLogger(main_logger).debug
        context.log.warn = logging.getLogger(main_logger).warning
        context.log.exception = logging.getLogger(main_logger).exception
        context.log.status = self._status
        context.log.finish = self._finish

    def _status(self, message, count = None, total = None):
        if count == None:
            print message.encode('utf-8')
        else:
            if self.verbose > 0:
                print message + ' [%d out of %d]' % (count, total)
            else:
                if ( count == 1 and total != None and total > 1 ) or ( total != self.pbtotal and total > 1):
                    self.progressbar = CursorVisibleChargingBar('Processing', max=total, suffix='%(percent)d%% [%(index)d/%(max)d]', width=48)
                    self.pbtotal = total
                    self.progressbar.goto(count-1)
                if count > 1:
                    self.progressbar.next()

    def _finish(self, message = 'Finished'):
        if self.verbose <= 0 and hasattr(self, 'progressbar'):
            self.progressbar.finish()
            self.progressbar.clearln()
        else:
            print message.encode('utf-8')
