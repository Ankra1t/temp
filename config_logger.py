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

# # # # # ЛОГИРОВАНИЕ ОТПРАВКИ
# Отправленные с ошибкой
log_send_fails = logging.getLogger('log_send_fails')
log_send_fails.setLevel(logging.INFO)
handler_fileout_sendlog = TimedRotatingFileHandler(filename=os.path.join("logs/sendlog", "log_send_fails.log"), when='H', interval=8,
                                           backupCount=12, encoding='utf-8')
handler_fileout_sendlog.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
log_send_fails.addHandler(handler_fileout_sendlog)

# Тем кому не отправлять
log_send_no_send = logging.getLogger('log_send_no_send')
log_send_no_send.setLevel(logging.INFO)
handler_fileout_no_send = TimedRotatingFileHandler(filename=os.path.join("logs/sendlog", "log_send_no_send.log"), when='H', interval=8,
                                           backupCount=12, encoding='utf-8')
handler_fileout_no_send.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
log_send_no_send.addHandler(handler_fileout_no_send)

# Список отправки
log_send_ok = logging.getLogger('log_send_ok')
log_send_ok.setLevel(logging.INFO)
handler_fileout_send_ok = TimedRotatingFileHandler(filename=os.path.join("logs/sendlog", "log_send_send_ok.log"), when='H', interval=8,
                                           backupCount=12, encoding='utf-8')
handler_fileout_send_ok.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
log_send_ok.addHandler(handler_fileout_send_ok)