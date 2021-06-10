from vk_messages import MessagesAPI
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False)
print("Вход выполнен")
from_id = int(messages.cookies_final['l'])

user_id = input("Введите ID пользователя: ")

history = messages.method('messages.getHistory', user_id=user_id, count=1)

message_to_search = input("Введите сообщение на которое будем отвечать:\n").lower()
message_to_send = input("Введите сообщение которое будем отправлять:\n")

while True:
    history = messages.method('messages.getHistory', user_id=user_id, count=1)
    last_msg_text = history['items'][0]['text']
    last_msg_id = history['items'][0]['from_id']
    if last_msg_id != from_id:
        if last_msg_text == message_to_search:
            messages.method('messages.send', user_id=user_id, message=message_to_send, random_id=get_random())
            print(f'Отправлено сообщение "{message_to_send}"')
