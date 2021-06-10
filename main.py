from vk_messages import MessagesAPI
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD



messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False)
print("Вход выполнен")
from_id = int(messages.cookies_final['l'])

print('Вводите ID пользователей, для прекращения ввода введите 0')
user_id = input()
user_id_set = set()
user_id_list = list()
while user_id != '0':
    user_id_set.add(user_id)
    user_id = input()

message_to_search = input("Введите сообщение на которое будем отвечать:\n").lower()
message_to_send = input("Введите сообщение которое будем отправлять:\n")


for user in user_id_set:
    temp_history = messages.method('messages.getHistory', user_id=user, count=1)
    try:
        get_msg = temp_history['items'][0]['text']
    except IndexError:
        print(f'Диалог с пользователем {user} не найден, пользователь удален из списка')
        continue
    user_id_list.append(user)

print(f'Бот активирован для пользователей {user_id_list}')
while True:
    for user_id in user_id_list:
        history = messages.method('messages.getHistory', user_id=user_id, count=1)
        last_msg_text = history['items'][0]['text']
        last_msg_id = history['items'][0]['from_id']
        if last_msg_id != from_id:
            if last_msg_text == message_to_search:
                messages.method('messages.send', user_id=user_id, message=message_to_send, random_id=get_random())
                print(f'Отправлено сообщение "{message_to_send}" пользователю с ID {user_id}')
