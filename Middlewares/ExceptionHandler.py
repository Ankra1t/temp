from telebot import ExceptionHandler

from config_logger import logger

class ExHandler(ExceptionHandler):
    def handle(self, e):
        logger.error(f'Uncaught bot error -> {e}')