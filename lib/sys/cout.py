from logging.handlers import SysLogHandler
import tempfile
import logging
import sys
import os

class CLIHandler(object):
    LEVELS = [logging.WARN, logging.INFO, logging.DEBUG, logging.DEBUG]

    def __init__(self, context):
        self.verbose = context.verbose
        if sys.platform == 'darwin':
            address = '/var/run/syslog'
        else:
            address = '/dev/log'
        tempfile_handle, self.tempfile = tempfile.mkstemp(prefix=os.path.basename(sys.argv[0]))
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(name)s.%(module)s.%(funcName)s: [%(levelname)s] %(message)s',
                datefmt='%m-%d %H:%M',
                filename=self.tempfile,
                filemode='w')
        syslog_logger = SysLogHandler(address = address, facility='local1')
        syslog_logger.setLevel(logging.DEBUG)
        syslog_formatter = logging.Formatter('%(module)s.%(funcName)s[%(process)s]: (%(levelname)s) %(message)s')
        syslog_logger.setFormatter(syslog_formatter)
        logging.getLogger('internal-syslog').addHandler(syslog_logger)
        logging.getLogger('internal-syslog').warn('Debug logfile initialized at %s' % self.tempfile)
        console_logger = logging.StreamHandler()
        console_logger.setLevel(CLIHandler.LEVELS[self.verbose])
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s - |%(name)s.%(module)s|')
        console_logger.setFormatter(console_formatter)
        main_logger = 'main' if self.verbose < 3 else ''
        logging.getLogger(main_logger).addHandler(console_logger)
        self.log = context.log = type('', (), {})()
        context.log.info = logging.getLogger(main_logger).info
        context.log.error = logging.getLogger(main_logger).error
        context.log.debug = logging.getLogger(main_logger).debug
        context.log.warn = logging.getLogger(main_logger).warning
        context.log.exception = logging.getLogger(main_logger).exception
        context.log.status = self._status

    def _status(self, message, count, total):
        self.log.info(message + ' [%d out of %d]' % (count, total))
