from vk_messages import MessagesAPI, vk_messages
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD
from get_objects import *
from sys import exit
from time import sleep
import vk_api


def get_img(path):
    image = 'memes/'
    image += choice(path)
    attachments = list()
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    return ','.join(attachments)


def fill_commands_list(history, i):
    global commands
    last_msg_text = history['items'][i]['text']
    last_msg_id = history['items'][i]['from_id']
    msg_id = history['items'][i]['id']
    if msg_id in msg_ids_set:
        return
    msg_ids_set.add(msg_id)
    if last_msg_text.lower() in ['!выкл', '!пауза']:
        if last_msg_id == my_id:
            commands.append(last_msg_text.lower())
            msg_ids_set.add(msg_id)
            return
    elif last_msg_text.lower() in ['!мем', '!команды']:
        commands.append(last_msg_text.lower())
        msg_ids_set.add(msg_id)
        return


def do_request(id_user):
    global commands, active
    n = 5
    #  Получаем 5 последних сообщений с пользователем id_user
    history = messages.method('messages.getHistory', user_id=id_user, count=n)

    commands = list()
    for i in range(n):
        fill_commands_list(history, i)

    for i, cmd in enumerate(reversed(commands)):
        if isinstance(cmd, str):
            if cmd == '!пауза':
                if active:
                    message = 'поставил на паузу'
                    active = False
                else:
                    message = 'снял с паузы'
                    active = True
                messages.method(name='messages.send',
                                peer_id=id_user,
                                message=message,
                                random_id=get_random())
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S> ")} {message}')

            if cmd == '!выкл':
                messages.method(name='messages.send',
                                peer_id=id_user,
                                message='все, пиздец, бот умер',
                                random_id=get_random())
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S> ")} отключение бота')
                exit()

            if active:
                if cmd == '!мем':
                    messages.method(name='messages.send',
                                    peer_id=id_user,
                                    attachment=get_img(mem_list),
                                    random_id=get_random())
                    print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} отправлена картинка')


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk_session)


print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

#  Получаем ID пользователя, с которого будут отправляться сообщения
my_id = vk.users.get(name_case='gen')[0]['id']

user_id_set = get_chats()
mem_list = listdir('memes')
correct_user_id_set = set()
commands = list()
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

active = True

while True:
    new_mem = listdir('memes')
    if new_mem != mem_list:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} memes update')
        mem_list = new_mem
    try:
        for usr_id in correct_user_id_set:
            do_request(usr_id)
    except vk_messages.Exception_MessagesAPI:
        print(vk_messages.Exception_MessagesAPI)
        sleep(10)

