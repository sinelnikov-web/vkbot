import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os
from threading import Thread
from datetime import datetime
import sqlite3

token = os.environ.get('BOT_TOKEN')
teacher_token = os.environ.get('TEACHER_TOKEN')
class TeachersDB:

    def __init__(self):
        self.db = sqlite3.connect('teachers.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS teachers_id(
                            id BIGINT)""")
        self.db.commit()

    def add_teacher(self, teacher_id):
        self.cursor.execute(f'SELECT id FROM teachers_id WHERE id = {teacher_id}')
        if self.cursor.fetchone() is None:
            self.cursor.execute(f'INSERT INTO teachers_id VALUES({teacher_id})')
            self.db.commit()
            for value in self.cursor.execute('SELECT id FROM teachers_id'):
                print(value)

    async def check_teacher(self, teacher_id):
        self.cursor.execute(f'SELECT id FROM teachers_id WHERE id = {teacher_id}')
        if self.cursor.fetchone() is None:
            send_message(teacher_id, 'Введите уникальный ключ учителя')
            while True:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            if event.user_id == teacher_id:
                                if event.text == teacher_token:
                                    self.add_teacher(teacher_id)
                                    send_message(teacher_id, 'Вы успешно авторизовались')
                                    return True
                                else:
                                    send_message(teacher_id, 'Неверный ключ')
                                    return False
        else:
            send_message(teacher_id, 'Вы успешно авторизовались')
            return True

    def delete_teacher(self, teacher_id):
        self.cursor.execute(f"DELETE FROM teachers_id WHERE id = {teacher_id}")

teachers_database = TeachersDB()

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_message(user_id, text):
    vk_session.method('messages.send',
                      {'user_id': user_id,
                       'message': text,
                       'random_id': 0})

async def check_user(user_id):
    return await teachers_database.check_teacher(user_id)

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if event.text == 'учитель':
                    check = check_user(event.user_id)
                    if check:
                        send_message(event.user_id, 'Что бы вы хотели сделать?')

                elif event.text == 'ученик':
                    send_message(event.user_id, 'выбирай предмет')

                elif event.text == 'удалить':
                    teachers_database.delete_teacher(event.user_id)
                    send_message(event.user_id, 'Вы удалены')
                else:
                    send_message(event.user_id, 'неизвестная комманда')
