import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os
import sqlite3
import json

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

    def check_teacher(self, teacher_id):
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
                                    send_message(teacher_id, 'Вы успешно авторизовались \n Выбирайте ваш предмет', keyboard=subjects_keyboard)
                                    return True
                                else:
                                    send_message(teacher_id, 'Неверный ключ')
                                    return False
        else:
            send_message(teacher_id, 'Вы успешно авторизовались \n Выбирайте ваш предмет.', keyboard=subjects_keyboard)
            return True

    def delete_teacher(self, teacher_id):
        self.cursor.execute(f"DELETE FROM teachers_id WHERE id = {teacher_id}")
        self.db.commit()

teachers_database = TeachersDB()
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

default_keyboard = {
    "one_time": None,
    "buttons": [
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Учитель"
                },
                "color": "positive"
        }],
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Ученик"
                },
                "color": "primary"
        }]
    ]
}

subjects_keyboard = {
    "one_time": None,
    "buttons": [
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Математика"
                },
                "color": "positive"
        },
        {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Русский язык"
                },
                "color": "primary"
        }],
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Английский язык"
                },
                "color": "positive"
        },
        {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Казахский язык"
                },
                "color": "primary"
        }],
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Физика"
                },
                "color": "positive"
        },
        {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "География"
                },
                "color": "primary"
        }],
        [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Назад"
                },
                "color": "negative"
        }]
    ]
}


def send_message(user_id, text, keyboard = None):
    vk_session.method('messages.send',
                      {'user_id': user_id,
                       'message': text,
                       'keyboard': None if keyboard == None else json.dumps(keyboard, ensure_ascii=False),
                       'random_id': 0})

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if event.text.lower() == 'начать' or event.text.lower() == 'назад':
                    send_message(event.user_id, 'Выбирай', default_keyboard)
                elif event.text.lower() == 'учитель':
                    check = teachers_database.check_teacher(event.user_id)
                elif event.text.lower() == 'ученик':
                    send_message(event.user_id, 'выбирай предмет', subjects_keyboard)
                elif event.text.lower() == 'удалить':
                    teachers_database.delete_teacher(event.user_id)
                    send_message(event.user_id, 'Вы удалены')
                else:
                    send_message(event.user_id, 'неизвестная комманда')
