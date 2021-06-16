from bs4 import BeautifulSoup
from random import choice, random
from settings import TT_KEY, YANDEX_API_KEY
from requests import get
import requests


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
    except requests.exceptions.MissingSchema:
        return
    except requests.exceptions.InvalidURL:
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


def get_weather_today():

    headers = {'X-Yandex-API-Key': YANDEX_API_KEY}

    params = {
        'lat': '43.11981',
        'lon': '131.88692',
        'lang': 'ru_RU',
        'extra': 'true'}

    url = 'https://api.weather.yandex.ru/v2/forecast?'
    res = requests.get(url=url, headers=headers, params=params)

    json = res.json()

    temp = json['fact']['temp']

    condition_dict = {
        'clear': 'ясно',
        'partly-cloudy': 'малооблачно',
        'cloudy': 'облачно с прояснениями',
        'overcast': 'пасмурно',
        'drizzle': 'морось',
        'light-rain': 'небольшой дождь',
        'rain': 'дождь',
        'moderate-rain': 'умеренно сильный дождь',
        'heavy-rain': 'сильный дождь',
        'continuous-heavy-rain': 'длительный сильный дождь',
        'showers': 'ливень',
        'wet-snow': 'дождь со снегом',
        'light-snow': 'небольшой снег',
        'snow': 'снег',
        'snow-showers': 'снегопад',
        'hail': 'град',
        'thunderstorm': 'гроза',
        'thunderstorm-with-rain': 'дождь с грозой',
        'thunderstorm-with-hail': 'гроза с градом'}

    condition = condition_dict[json['fact']['condition']]

    return f'В городе Владивосток{temp}°C, {condition}'


def get_weather_tomorrow():
    string = ""
    headers = {'X-Yandex-API-Key': '53621d53-cb19-4d95-b810-c5b295478eeb'}
    params = {
        'lat': '43.11981',
        'lon': '131.88692',
        'lang': 'ru_RU',
        'limit': '2',
        'extra': 'true'}

    url = 'https://api.weather.yandex.ru/v2/forecast?'
    res = requests.get(url=url, headers=headers, params=params)
    condition_dict = {
        'clear': 'ясно',
        'partly-cloudy': 'малооблачно',
        'cloudy': 'облачно с прояснениями',
        'overcast': 'пасмурно',
        'drizzle': 'морось',
        'light-rain': 'небольшой дождь',
        'rain': 'дождь',
        'moderate-rain': 'умеренно сильный дождь',
        'heavy-rain': 'сильный дождь',
        'continuous-heavy-rain': 'длительный сильный дождь',
        'showers': 'ливень',
        'wet-snow': 'дождь со снегом',
        'light-snow': 'небольшой снег',
        'snow': 'снег',
        'snow-showers': 'снегопад',
        'hail': 'град',
        'thunderstorm': 'гроза',
        'thunderstorm-with-rain': 'дождь с грозой',
        'thunderstorm-with-hail': 'гроза с градом'}
    days_dict = {
        'morning': 'Утром',
        'day': 'Днем',
        'evening': 'Вечером',
        'night': 'Ночью'
    }
    json = res.json()

    for i in days_dict:
        temp = json['forecasts'][1]['parts'][i]['temp_avg']
        condition = condition_dict[json['forecasts'][1]['parts'][i]['condition']]
        string += f'{days_dict[i]} - средняя температура {temp}°C, {condition}\n'

    return f'Завтра в городе Владивосток\n{string}'


def get_help_message():
    string = ''
    with open('help.txt', 'r', encoding='utf-8') as help_txt:
        for line in help_txt:
            string += line.strip()
            string += '\n'
    return string

