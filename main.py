from sys import exit
from datetime import datetime
from os import listdir, remove
import logging

from vk_messages import MessagesAPI, vk_messages
from vk_messages.utils import get_random
from requests import ConnectionError
from time import time, sleep
from http.client import RemoteDisconnected
import vk_api

from settings import *
from get_objects import *
from balaboba_class import YandexBalaboba


def get_img(index=None) -> str:
    """
    Если фунция вызвана без параметра - выбирается случайная картинка,
    иначе, картинка по индексу из списка.
    Дальше происходит загрузка картинки на сервер.
    Функция возвращает данные о картинке для последующей её отправки
    """
    image = 'memes/'
    if index is None:
        image += choice(mem_list)
    else:
        image += mem_list[index]
    attachments = list()
    upload_image = upload.photo_messages(photos=image)[0]
    attachments.append(f'photo{upload_image["owner_id"]}_{upload_image["id"]}')
    return ','.join(attachments)


def create_and_send_message(history, dialog_id):
    """
    Функция получает объект history и из него заполняет
    глобальный список словарями для последующих действий

    """
    global commands, active, start
    text_to_translate = None
    all_msg_logs = open(f'logs/vk_{dialog_id}.txt', 'a+', encoding='utf-8')
    last_msg_text = history['text']
    last_msg_id = history['from_id']
    msg_id = history['id']
    message = ""
    if last_msg_id not in id_info:
        id_info[last_msg_id] = dict(
            first_name=vk.users.get(name_case="dat", user_id=last_msg_id)[0]["first_name"],
            last_name=vk.users.get(name_case="dat", user_id=last_msg_id)[0]["last_name"])

    firstname = id_info[last_msg_id]['first_name']
    lastname = id_info[last_msg_id]['last_name']
    if msg_id in msg_ids_set:
        return
    all_msg_logs.write(datetime.now().strftime("<%d-%m-%Y %H:%M:%S> "))
    all_msg_logs.write(f'"{last_msg_text}" {vk.users.get(user_id=last_msg_id)[0]["first_name"]}'
                       f' {vk.users.get(user_id=last_msg_id)[0]["last_name"]}, MSG_ID: {msg_id}\n')
    msg_ids_set.add(msg_id)
    if last_msg_text.lower() in ['!выкл', '!пауза']:
        if last_msg_id in admins:

            if last_msg_text == '!пауза':
                if active:
                    message = 'поставил на паузу'
                    active = False
                else:
                    message = 'снял с паузы'
                    active = True
                messages.method(name='messages.send',
                                peer_id=last_msg_id,
                                message=message,
                                random_id=get_random())
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S> ")} {message}')
                msg_ids_set.add(msg_id)
                return

            elif last_msg_text == '!выкл':
                messages.method(name='messages.send',
                                peer_id=last_msg_id,
                                message='все, пиздец, бот умер',
                                random_id=get_random())
                print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S> ")} отключение бота')
                exit()

    elif last_msg_text.lower()[:4] == '!мем':
        if last_msg_text[4:] != '':
            try:
                if int(last_msg_text[4:]) <= len(mem_list):
                    attach = get_img(int(last_msg_text[4:]) - 1)
                else:
                    attach = get_img()
            except ValueError:
                attach = get_img()
        else:
            attach = get_img()
        messages.method(name='messages.send',
                        peer_id=dialog_id,
                        attachment=attach,
                        random_id=get_random())
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} отправлена картинка')
        msg_ids_set.add(msg_id)
        return
    elif last_msg_text.lower()[:10] == '!перевести':
        text_to_translate = ' '.join(last_msg_text.split()[1:])
        last_msg_text = '!перевести'
        msg_ids_set.add(msg_id)

    if last_msg_id not in admins or last_msg_text in ['!монетка', '!погода', '!статус', '!помощь',
                                                      '!погода_завтра', '!биткоин', '!перевести', '!roll',
                                                      '!погода_сегодня']:
        commands_dict = {
            '!погода': get_weather_today,
            '!roll': roll,
            '!помощь': get_help_message,
            '!биткоин': get_btc_price,
        }
        if history['attachments']:
            if history['attachments'][0]['type'] == 'audio_message':
                if history['attachments'][0]['audio_message']['owner_id'] == 144322116:
                    message = 'вау, это же приятный голос, давайте послушаем'
                else:
                    message = 'че распизделся блять, тебе буквы для чего изобрели, что бы мы это вот слушали здесь?'
        elif last_msg_text == '!монетка':
            if last_msg_id == 299158076:
                message = coin_flip_fedya()
            else:
                message = coin_flip()
        elif last_msg_text == '!перевести':
            message = translate(text_to_translate)
        elif last_msg_text == '!погода_завтра':
            message = get_weather_tomorrow()
        elif last_msg_text == '!погода_сегодня':
            message = get_weather_tomorrow(0)
        elif last_msg_text == '!статус':
            message = get_time_info(int(time() - start))
        elif last_msg_text in commands_dict:
            message = commands_dict[last_msg_text]()
        elif 'tiktok' in last_msg_text:
            if get_ticktok_nickname(last_msg_text) == 'holovoda0':
                message = 'ваааааау тиктоки от полины всем смотреть'
            else:
                message = 'вам в мозги насрали, а вы и ради тиктоки смотреть'
        else:
            if random() >= 0.25:
                msg_ids_set.add(msg_id)
                all_msg_logs.close()
                return
            message = balaboba_answer(last_msg_text)
            if message is None:
                return

        if active:
            if message[:20] == 'В городе Владивосток':
                if last_msg_id == 144322116:
                    msg_id = 934734
            messages.method('messages.send',
                            peer_id=dialog_id,
                            message=message,
                            random_id=get_random(),
                            reply_to=msg_id)
            print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} '
                  f'Отправлено сообщение "{message}" {firstname} {lastname}')

        msg_ids_set.add(msg_id)
    all_msg_logs.close()
    return


def sending_msg(id_user):
    """
    Функция отправляет сообщения исходя из данных словаря,
    который заполняет функция fill_commands_list
    """
    global commands, active
    n = 5
    #  Получаем n последних сообщений с пользователем id_user
    history = messages.method('messages.getHistory', user_id=id_user, count=n)
    history_items = list()
    for i in range(n):
        history_items.append(history['items'][i])
    for i in history_items:
        create_and_send_message(i, id_user)


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk_session)

print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} bot started')
print(f"Выполнен вход в аккаунт {vk.users.get(name_case='gen')[0]['first_name']} "
      f"{vk.users.get(name_case='gen')[0]['last_name']}")

my_id = vk.users.get(name_case='gen')[0]['id']
admins = [201675606, my_id]
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
    if new_mem != mem_list:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} memes update')
        mem_list = new_mem
    try:
        for usr_id in correct_user_id_set:
            sending_msg(usr_id)
    except vk_messages.Exception_MessagesAPI as ex:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")}\n{ex}')
        logger.exception(ex)
        sleep(10)
    except AttributeError:
        print(f'{datetime.now().strftime("<%d-%m-%Y %H:%M:%S>")} error, trying login again')
        remove('sessions/' + listdir('sessions')[0])
        messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False, cookies_save_path='sessions/')
    except RemoteDisconnected as ex:
        logger.exception(ex)
        pass
    except ConnectionError as ex:
        logger.exception(ex)
        pass
    except Exception as e:
        logger.exception(e)
        continue
