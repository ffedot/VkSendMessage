from vk_messages import MessagesAPI
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD, TT_KEY
from datetime import datetime
from time import sleep
from get_objects import *
import vk_api


def create_help():
    help_msg = ''
    for k in answers.keys():
        if k == TT_KEY:
            continue
        help_msg += k
        help_msg += '\n'
    return help_msg


def do_request(id_user, from_id):
    #  Получаем 5 последних сообщений с пользователем id_user
    history = messages.method('messages.getHistory', user_id=id_user, count=5)

    #  Если ID отправителя этого сообщения не равен нашему
    for i in range(5):
        last_msg_text = history['items'][i]['text']
        last_msg_id = history['items'][i]['from_id']
        msg_id = history['items'][i]['id']
        #  Добавляем ID сообщения во множество, что бы не отвечать повторно на сообщения по нескольку раз
        if msg_id in msg_ids_set:
            continue
        #  Распечатка всех возможных команд
        if last_msg_text.lower() == '!команды':
            messages.method('messages.send', peer_id=id_user, message=create_help(), random_id=get_random(),
                            reply_to=msg_id)
            msg_ids_set.add(msg_id)
            break
        #  Если последнее сообщение не от нас
        if last_msg_id != from_id:
            #  Если последнее сообщение содержит tiktok
            if 'tiktok' in last_msg_text.lower():
                #  Получение никнейма тикток отправителя
                if get_ticktok_nickname(last_msg_text) == 'holodova0':
                    last_msg_text = TT_KEY
                else:
                    last_msg_text = 'tiktok'
            if last_msg_text.lower() in answers:
                firstname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"]
                lastname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"]
                messages.method('messages.send', peer_id=id_user, message=answers[last_msg_text.lower()],
                                random_id=get_random(), reply_to=msg_id)
                msg_ids_set.add(msg_id)
                print(f'Отправлено сообщение "{answers[last_msg_text.lower()]}" {firstname} {lastname}')
                logfile = open('log.txt', 'a+', encoding='utf-8')
                logfile.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
                logfile.write(f'Отправлено сообщение "{answers[last_msg_text.lower()]}" {firstname} {lastname}, '
                              f'ID: {last_msg_id}\n')
                logfile.close()


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()

print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

#  Получаем ID пользователя, с которого будут отправляться сообщения
my_id = vk.users.get(name_case='gen')[0]['id']

answers = get_answers()
user_id_set = get_chats()
correct_user_id_set = set()
msg_ids_set = set()


#  Проходим по всему множеству с ID и пытаемся полчить последнее сообщение, если срабатывает исключение,
#  значит диалога нет, если исключение не сработало, добавляем в список ID
for user in user_id_set:
    temp_history = messages.method('messages.getHistory', user_id=user, count=1)
    try:
        get_msg = temp_history['items'][0]['text']
    except IndexError:
        print(f'Диалог с пользователем {user} не найден, пользователь удален из списка')
        continue
    correct_user_id_set.add(user)

# Вывод оповещения для активации для каждого пользователя
for user in correct_user_id_set:
    first_name = vk.users.get(name_case='gen', user_ids=user)[0]['first_name']
    last_name = vk.users.get(name_case='gen', user_ids=user)[0]['last_name']
    print(f'Бот активирован для {first_name} {last_name}')


while True:
    for usr_id in correct_user_id_set:
        do_request(usr_id, my_id)
    sleep(1)
