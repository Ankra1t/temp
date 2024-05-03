import traceback
from telebot import ExceptionHandler

from config_logger import logger

class ExHandler(ExceptionHandler):
    def handle(self, e):
        print(traceback.format_exc())
        logger.error(f'Uncaught bot error -> {e}')