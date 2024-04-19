from datetime import datetime

from db import Database
from models import Task, TaskMessage



class ServiceTasks(object):
    """Класс для работы с тарифами"""

    def __init__(self, db: Database) -> None:
        self.db = db

    # # # # # # Создание заданий
    def plan_task(self, task: Task):
        self.db.set_task(task)

    def plan_message(self, user_id: int, time: datetime, message: str):
        task = Task()
        task.user_id = user_id
        task.type_task = 'send_message_start_trial'
        task.date_action = time
        task.message = TaskMessage()
        task.message.type_message = 'text'
        task.message.text = message
        task.active = 1

        self.plan_task(task)

    # # # # # # Получение и выполнение заданий
    def check_during_task(self, type: str):
        """Проверить и получить задания для выполнения"""
        
        pass

    # # # # # # Удаление заданий
    def del_task(self, task: int | Task):
        pass
    

