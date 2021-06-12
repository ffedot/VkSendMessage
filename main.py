from vk_messages import MessagesAPI, vk_messages
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD
from datetime import datetime
from get_objects import *
from sys import exit
from os import listdir
from time import sleep
import vk_api


def get_img(path):
    image = 'mems/'
    image += choice(path)
    attachments = list()
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    return attachments


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
    all_msg_logs = open('all_msg_logs.txt', 'a+', encoding='utf-8')
    #  Если ID отправителя этого сообщения не равен нашему
    for i in reversed(range(5)):
        last_msg_text = history['items'][i]['text']
        last_msg_id = history['items'][i]['from_id']
        msg_id = history['items'][i]['id']
        #  Добавляем ID сообщения во множество, что бы не отвечать повторно на сообщения по нескольку раз
        if msg_id in msg_ids_set:
            continue
        all_msg_logs.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
        all_msg_logs.write(f'"{last_msg_text}" {vk.users.get(user_id=last_msg_id)[0]["first_name"]}'
                           f' {vk.users.get(user_id=last_msg_id)[0]["last_name"]}, MSG_ID: {msg_id}\n')
        msg_ids_set.add(msg_id)
        #  Распечатка всех возможных команд
        if last_msg_text.lower() == '!команды':
            messages.method('messages.send', peer_id=id_user, message=create_help(), random_id=get_random())
            print('Отправлен список команд')
            msg_ids_set.add(msg_id)
            continue
        elif last_msg_text.lower() == '!мем':
            messages.method('messages.send', peer_id=id_user, attachment=','.join(get_img(mem_list)),
                            random_id=get_random())
            msg_ids_set.add(msg_id)
            print('Отправлена картинка')
            continue
        elif last_msg_text.lower() == 'ab6dfb89f46d898bb3896f397fd801cf363c3c2559e8dc65cc2b96445257b262':
            messages.method('messages.send', peer_id=id_user, message='все бот умер', random_id=get_random())
            exit()
        #  Если последнее сообщение не от нас
        elif last_msg_id != from_id:
            #  Функция разбивает сообщение по пробелам, обходит все слова, если они есть в словаре - возращает ключ
            #  Иначе возвращает False
            last_msg_text = get_key(last_msg_text, answers)
            if last_msg_text:
                #  Если по ключу находится список, то мы выбираем случайный его элемент
                if isinstance(answers[last_msg_text], list):
                    message = choice(answers[last_msg_text])
                else:
                    message = answers[last_msg_text.lower()]
                firstname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"]
                lastname = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"]
                messages.method('messages.send', peer_id=id_user, message=message,
                                random_id=get_random(), reply_to=msg_id)
                msg_ids_set.add(msg_id)
                print(f'Отправлено сообщение "{message}" {firstname} {lastname}')
                logfile = open('log.txt', 'a+', encoding='utf-8')
                logfile.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
                logfile.write(f'Отправлено сообщение "{message}" {firstname} {lastname}, '
                              f'ID: {last_msg_id}\n')
                logfile.close()
    all_msg_logs.close()


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk_session)


print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

#  Получаем ID пользователя, с которого будут отправляться сообщения
my_id = vk.users.get(name_case='gen')[0]['id']

answers = get_answers()
user_id_set = get_chats()
mem_list = listdir('mems')
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
    try:
        for usr_id in correct_user_id_set:
            do_request(usr_id, my_id)
    except vk_messages.Exception_MessagesAPI:
        print(vk_messages.Exception_MessagesAPI)
        sleep(10)
