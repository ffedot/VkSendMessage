from bs4 import BeautifulSoup
from requests import get, exceptions
from random import choice, random
from settings import TT_KEY
from settings import PYOWM_KEY
from pyowm.utils.config import get_default_config
from requests import get
import os
import pyowm


def create_files():
    if not os.path.exists('memes'):
        os.mkdir('memes')
    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if not len(os.listdir('memes')):
        img = 'https://memepedia.ru/wp-content/uploads/2020/09/dzheremi-klarkson-mem.png'
        p = get(img)
        out = open('memes/mem01.png', 'wb')
        out.write(p.content)
        out.close()

    if not os.path.exists('help.txt'):
        file = open('help.txt', 'w')
        file.close()

    if not os.path.exists('log.txt'):
        file = open('log.txt', 'w')
        file.close()

    if not os.path.exists('all_msg_logs.txt'):
        file = open('all_msg_logs.txt', 'w')
        file.close()

    if not os.path.exists('ids.txt'):
        file = open('ids.txt', 'w')
        file.close()

    if not os.path.exists('answers_all.txt'):
        file = open('answers_all.txt', 'w')
        file.close()

    if not os.path.exists('answers_polina.txt'):
        file = open('answers_polina.txt', 'w')
        file.close()

    if not os.path.exists('.env'):
        file = open('.env', 'w')
        file.write('LOGIN=\n')
        file.write('PASSWORD=\n')
        file.write('PYOWM_KEY=\n')


def coin_flip():
    if random() >= 0.7:
        return 'Решка'
    return 'Орел'


def get_chats():
    user_id_set = set()
    with open('ids.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if line[0].strip() == '#':
                continue
            user_id_set.add(line.strip())
    return user_id_set


def get_ticktok_nickname(url: str):
    headers = {
        'Accept': '*/*',
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 YaBrowser/21.5.2.638 Yowser/2.5 Safari/537.36'
    }
    try:
        req = get(url, headers=headers)
    except exceptions.MissingSchema:
        return
    except exceptions.InvalidURL:
        return
    src = req.text

    soup = BeautifulSoup(src, "lxml")
    page_h3 = soup.find("body")

    temp_list = list()
    c = 0
    for i in page_h3:
        temp_list.append(str(i))
        c += 1
        if c == 2:
            break
    temp_list.pop(0)

    my_str = temp_list[0]

    nickname = my_str[my_str.find('@') + 1:my_str.find('/', 213)]
    return nickname


def get_answers(filename: str):
    answers = dict()
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line[0].strip() == '#':
                continue
            s = line.strip().split(':')
            temp = edit_dict(s[1][1:])
            if isinstance(temp, list):
                answers[s[0][:-1]] = temp
            else:
                answers[s[0][:-1]] = s[1][1:]
    return answers


def edit_dict(ans):
    if ans[0] in ['[', ']'] and ans[-1] in ['[', ']']:
        return no_spaces(ans[1:-1].split(';'))


def no_spaces(s):
    t = list()
    for i in s:
        if i[0] == ' ':
            t.append(i[1:])
            continue
        t.append(i)
    return t


def get_key(msg: str, answers: dict):
    if msg == '':
        return
    signs = [',', '.', '!', '?', '-', ';', ':', '_', '«', '»', ')', '(', '…', '-']
    if 'tiktok' in msg.lower():
        if get_ticktok_nickname(msg) == 'holodova0':
            return TT_KEY
        return 'tiktok'
    random_ans = set()
    if msg not in answers:
        msg_list = msg.split(' ')
        for i in msg_list:
            while i[-1] in signs:
                i = i[:-1]
            if i.lower() in answers:
                random_ans.add(i)
        for i in msg_list:
            if '&' in i:
                if i[i.find('&'):i.find(';')] in answers:
                    random_ans.add(i[i.find('&'):i.find(';')])
    else:
        return msg
    if len(random_ans) != 0:
        return choice(list(random_ans)).lower()
    return False


def get_time_str(number: int, t: str):
    words_str = {'s': ['секунду', 'секунды', 'секунд'],
                 'm': ['минуту', 'минуты', 'минут'],
                 'h': ['час', 'часа', 'часов'],
                 'd': ['день', 'дня', 'дней']
                 }
    if number == 0:
        return ''
    if 10 <= number % 100 <= 20:
        return f'{number} {words_str[t][2]} '
    elif number % 10 == 1:
        return f'{number} {words_str[t][0]} '
    elif 2 <= number % 10 <= 4:
        return f'{number} {words_str[t][1]} '
    else:
        return f'{number} {words_str[t][2]} '


def get_time_info(seconds: int):
    return_string = 'Бот работает уже\n'
    s = (seconds % 3600) % 60
    m = (seconds % 3600) // 60
    h = seconds // 3600
    d = seconds // 3600 // 24
    words_int = [d, h, m, s]
    words_str = ['d', 'h', 'm', 's']
    while h > 23:
        d += 1
        h -= 24
    for i in range(len(words_int)):
        return_string += get_time_str(words_int[i], words_str[i])
    return return_string


def get_weather_message():
    config = get_default_config()
    config['language'] = 'ru'

    owm = pyowm.OWM(PYOWM_KEY, config)

    w = owm.weather_manager().weather_at_place('Vladivostok').weather

    temp_c = int(w.temperature('celsius')['temp'])

    return f'В городе Владивосток {temp_c}°C\n{w.detailed_status.title()}'


def get_help_message():
    string = ''
    with open('help.txt', 'r', encoding='utf-8') as help_txt:
        for line in help_txt:
            string += line.strip()
            string += '\n'
    return string

