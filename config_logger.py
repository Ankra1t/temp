import os
import sys
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
handler_stdout = StreamHandler(stream=sys.stdout)
handler_fileout = TimedRotatingFileHandler(filename=os.path.join("logs", "main_logs.log"), when='D', interval=1,
                                           backupCount=14, encoding='utf-8')
handler_stdout.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
handler_fileout.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler_stdout)
logger.addHandler(handler_fileout)