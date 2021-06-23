from vk_messages import MessagesAPI, vk_messages
from vk_messages.utils import get_random
from settings import *
from get_objects import *
from sys import exit
from time import sleep, time
from datetime import datetime
from os import listdir, remove
from requests import ConnectionError
from http.client import RemoteDisconnected
import vk_api
import logging


def get_img(index=999999):
    image = 'memes/'
    if index == 999999:
        image += choice(mem_list)
    else:
        image += mem_list[index]
    attachments = list()
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    return ','.join(attachments)


def fill_commands_list(history, dialog_id):
    global commands
    all_msg_logs = open(f'logs/vk_{dialog_id}.txt', 'a+', encoding='utf-8')
    last_msg_text = history['text']
    last_msg_id = history['from_id']
    msg_id = history['id']
    if msg_id in msg_ids_set:
        return
    all_msg_logs.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
    all_msg_logs.write(f'"{last_msg_text}" {vk.users.get(user_id=last_msg_id)[0]["first_name"]}'
                       f' {vk.users.get(user_id=last_msg_id)[0]["last_name"]}, MSG_ID: {msg_id}\n')
    msg_ids_set.add(msg_id)
    if last_msg_text.lower() in ['!выкл', '!пауза']:
        if last_msg_id in admins:
            commands.append(last_msg_text.lower())
            msg_ids_set.add(msg_id)
            return
    elif last_msg_text.lower()[:4] == '!мем':
        commands.append(last_msg_text.lower())
        msg_ids_set.add(msg_id)
        return

    if history['attachments']:
        if history['attachments'][0]['type'] == 'audio_message':
            if history['attachments'][0]['audio_message']['owner_id'] == 144322116:
                last_msg_text = 'audio_message_polina'
            else:
                last_msg_text = 'audio_message_not_polina'
    if last_msg_id not in admins or last_msg_text in ['!монетка', '!погода', '!статус', '!помощь',
                                                      '!погода_завтра', '!биткоин']:
        temp_dictionary = dict()
        if last_msg_id != 144322116:
            answers = answers_all
        else:
            answers = answers_polina
        last_msg_text = get_key(last_msg_text, answers)
        if last_msg_text:
            if isinstance(answers[last_msg_text], list):
                temp_dictionary['message'] = choice(answers[last_msg_text])
            elif last_msg_text == '!монетка':
                if last_msg_id == 299158076:
                    temp_dictionary['message'] = coin_flip()
                else:
                    temp_dictionary['message'] = coin_flip2()
            elif last_msg_text == '!погода':
                temp_dictionary['message'] = get_weather_today()
            elif last_msg_text == '!погода_завтра':
                temp_dictionary['message'] = get_weather_tomorrow()
            elif last_msg_text == '!биткоин':
                temp_dictionary['message'] = get_btc()
            elif last_msg_text == '!помощь':
                temp_dictionary['message'] = get_help_message()
            elif last_msg_text == '!статус':
                temp_dictionary['message'] = get_time_info(int(time() - start))
            else:
                temp_dictionary['message'] = answers[last_msg_text.lower()]
            if last_msg_id not in id_info:
                id_info[last_msg_id] = dict(
                    first_name=vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"],
                    last_name=vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"])
            temp_dictionary['first_name'] = id_info[last_msg_id]['first_name']
            temp_dictionary['last_name'] = id_info[last_msg_id]['last_name']
            temp_dictionary['msg_id'] = msg_id
            temp_dictionary['last_msg_id'] = last_msg_id
        commands.append(temp_dictionary)
        msg_ids_set.add(msg_id)
    all_msg_logs.close()
    return


def sending_msg(id_user):
    global commands, active
    n = 5
    #  Получаем 5 последних сообщений с пользователем id_user
    history = messages.method('messages.getHistory', user_id=id_user, count=n)
    history_items = list()
    for i in range(n):
        history_items.append(history['items'][i])

    commands = list()
    for i in history_items:
        fill_commands_list(i, id_user)

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
                if cmd[:4] == '!мем':
                    if cmd[4:] != '':
                        try:
                            if int(cmd[4:]) <= len(mem_list):
                                attach = get_img(int(cmd[4:]) - 1)
                            else:
                                attach = get_img()
                        except ValueError:
                            attach = get_img()
                    else:
                        attach = get_img()
                    messages.method(name='messages.send',
                                    peer_id=id_user,
                                    attachment=attach,
                                    random_id=get_random())
                    print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} отправлена картинка')

        if isinstance(cmd, dict):
            if active:
                try:
                    firstname = cmd['first_name']
                except KeyError:
                    continue
                lastname = cmd['last_name']
                message = cmd['message']
                msg_id = cmd['msg_id']
                last_msg_id = cmd['last_msg_id']
                if message[:20] == 'В городе Владивосток':
                    if last_msg_id == 144322116:
                        msg_id = 934734
                messages.method('messages.send',
                                peer_id=id_user,
                                message=message,
                                random_id=get_random(),
                                reply_to=msg_id)
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} '
                      f'Отправлено сообщение "{message}" {firstname} {lastname}')
                logfile = open('txt/log.txt', 'a+', encoding='utf-8')
                logfile.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
                logfile.write(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} Отправлено сообщение "{message}" '
                              f'{firstname} {lastname}, ID: {last_msg_id}\n')
                logfile.close()


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk_session)


print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

#  Получаем ID пользователя, с которого будут отправляться сообщения
my_id = vk.users.get(name_case='gen')[0]['id']
admins = [201675606, my_id]
answers_all = get_answers('txt/all_answers.txt')
answers_polina = get_answers('txt/polina_answers.txt')
user_id_set = get_chats()
mem_list = listdir('memes')
correct_user_id_set = set()
commands = list()
msg_ids_set = set()
id_info = dict()


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

start = time()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler("logs/errors.txt")
formatter = logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


while True:
    if int(time() - start) % 1800 == 0:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")}')
    new_mem = listdir('memes')
    new_ans_a = get_answers('txt/all_answers.txt')
    new_ans_p = get_answers('txt/polina_answers.txt')
    if new_mem != mem_list:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} memes update')
        mem_list = new_mem
    if new_ans_a != answers_all or new_ans_p != answers_polina:
        answers_all = new_ans_a
        answers_polina = new_ans_p
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} answers update')
    try:
        for usr_id in correct_user_id_set:
            sending_msg(usr_id)
    except vk_messages.Exception_MessagesAPI as ex:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")}')
        sleep(10)
    except AttributeError:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} error, trying login again')
        remove('sessions/' + listdir('sessions')[0])
        messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
    except RemoteDisconnected:
        pass
    except ConnectionError:
        pass
    except Exception as e:
        logger.exception(e)
        continue
