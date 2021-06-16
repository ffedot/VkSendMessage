from vk_messages import MessagesAPI, vk_messages
from vk_messages.utils import get_random
from settings import *
from get_objects import *
from sys import exit
from time import sleep, time
from datetime import datetime
from os import listdir, remove
import vk_api


# TODO OTHER ACCOUNT
# TODO CREATE FOLDERS IF NOT EXIST
# TODO !погода
# TODO rework !команды


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


# def create_help():
#     help_msg = ''
#     for k in answers.keys():
#         if k == TT_KEY:
#             continue
#         if k[0] == '&':
#             continue
#         help_msg += k
#         help_msg += '\n'
#     return help_msg


def fill_commands_list(history, i):
    global commands
    all_msg_logs = open('all_msg_logs.txt', 'a+', encoding='utf-8')
    last_msg_text = history['items'][i]['text']
    last_msg_id = history['items'][i]['from_id']
    msg_id = history['items'][i]['id']
    if msg_id in msg_ids_set:
        return
    all_msg_logs.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
    all_msg_logs.write(f'"{last_msg_text}" {vk.users.get(user_id=last_msg_id)[0]["first_name"]}'
                       f' {vk.users.get(user_id=last_msg_id)[0]["last_name"]}, MSG_ID: {msg_id}\n')
    msg_ids_set.add(msg_id)
    if last_msg_text.lower() in ['!выкл', '!пауза']:
        if last_msg_id == my_id:
            commands.append(last_msg_text.lower())
            msg_ids_set.add(msg_id)
            return
    elif last_msg_text.lower() in ['!мем', '!команды', '!статус'] or last_msg_text.lower()[:4] == '!мем':
        commands.append(last_msg_text.lower())
        msg_ids_set.add(msg_id)
        return

    if history['items'][i]['attachments']:
        if history['items'][i]['attachments'][0]['type'] == 'audio_message':
            if history['items'][i]['attachments'][0]['audio_message']['owner_id'] == 144322116:
                last_msg_text = 'audio_message_polina'
            else:
                last_msg_text = 'audio_message_not_polina'
    if last_msg_id != my_id or last_msg_text in ['!монетка', '!погода']:
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
                temp_dictionary['message'] = coin_flip()
            elif last_msg_text == '!погода':
                temp_dictionary['message'] = get_weather_message()
            else:
                temp_dictionary['message'] = answers[last_msg_text.lower()]
            temp_dictionary['first_name'] = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"]
            temp_dictionary['last_name'] = vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"]
            temp_dictionary['msg_id'] = msg_id
            temp_dictionary['last_msg_id'] = last_msg_id
        commands.append(temp_dictionary)
        msg_ids_set.add(msg_id)
    all_msg_logs.close()
    return


def sending_msg(id_user):
    global commands, active
    n = 3
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

                # if cmd == '!команды':
                #     messages.method(name='messages.send',
                #                     peer_id=id_user,
                #                     message=create_help(),
                #                     random_id=get_random())
                #     print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} отправлены команды')

                if cmd == '!статус':
                    messages.method(name='messages.send',
                                    peer_id=id_user,
                                    message=get_time_info(int(time() - start)),
                                    random_id=get_random())
                    print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} отправлен uptime')

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
                messages.method('messages.send',
                                peer_id=id_user,
                                message=message,
                                random_id=get_random(),
                                reply_to=msg_id)
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} '
                      f'Отправлено сообщение "{message}" {firstname} {lastname}')
                logfile = open('log.txt', 'a+', encoding='utf-8')
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

answers_all = get_answers('answers_all.txt')
answers_polina = get_answers('answers_polina.txt')
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

start = time()
while True:
    if int(time() - start) % 1800 == 0:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")}')
        sleep(1)
    new_mem = listdir('memes')
    new_ans_a = get_answers('answers_all.txt')
    new_ans_p = get_answers('answers_polina.txt')
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
        print(ex)
        sleep(10)
    except AttributeError:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} error, trying login again')
        remove('sessions/' + listdir('sessions')[0])
        messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
