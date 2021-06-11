from vk_messages import MessagesAPI
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD
from datetime import datetime
import vk_api


def do_request(id_user, from_id):
    #  Получаем последнее сообщение с пользователем id_user
    history = messages.method('messages.getHistory', user_id=id_user, count=1)
    last_msg_text = history['items'][0]['text']
    last_msg_id = history['items'][0]['from_id']
    #  Если ID отправителя этого сообщения не равен нашему
    if last_msg_id != from_id:
        firstname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"]
        lastname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"]
        messages.method('messages.send', peer_id=id_user, message=last_msg_text, random_id=get_random(),
                        reply_to=history['items'][0]['id'])
        print(f'Отправлено сообщение "{last_msg_text}" {firstname} {lastname}')
        logfile = open('log.txt', 'a+', encoding='utf-8')
        logfile.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
        logfile.write(f'Отправлено сообщение "{last_msg_text}" {firstname} {lastname}, ID: {last_msg_id}\n')
        logfile.close()


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False)
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()

print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

#  Получаем ID пользователя, с которого будут отправляться сообщения
my_id = vk.users.get(name_case='gen')[0]['id']

print('Вводите ID пользователей, для прекращения ввода введите 0')
user_id = input()
user_id_set = set()
user_id_list = set()

while user_id != '0':
    user_id_set.add(user_id)
    user_id = input()

message_to_search = input("Введите сообщение на которое будем отвечать:\n").lower()
message_to_send = input("Введите сообщение которое будем отправлять:\n")

#  Проходим по всему множеству с ID и пытаемся полчить последнее сообщение, если срабатывает исключение,
#  значит диалога нет, если исключение не сработало, добавляем в список ID
for user in user_id_set:
    temp_history = messages.method('messages.getHistory', user_id=user, count=1)
    try:
        get_msg = temp_history['items'][0]['text']
    except IndexError:
        print(f'Диалог с пользователем {user} не найден, пользователь удален из списка')
        continue
    user_id_list.add(user)

# Вывод оповещения для активации для каждого пользователя
for user in user_id_list:
    first_name = vk.users.get(name_case='gen', user_ids=user)[0]['first_name']
    last_name = vk.users.get(name_case='gen', user_ids=user)[0]['last_name']
    print(f'Бот активирован для {first_name} {last_name}')

while True:
    for usr_id in user_id_list:
        do_request(usr_id, my_id)
