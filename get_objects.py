from bs4 import BeautifulSoup
from random import choice, random
from settings import TT_KEY, YANDEX_API_KEY, PYOWM_KEY
from requests import get
from pyowm.utils.config import get_default_config
from translate import Translator
import requests
import pickle
import json
import os
import pyowm


def coin_flip():
    if random() >= 0.7:
        return 'Решка'
    return 'Орел'


def coin_flip2():
    if random() >= 0.5:
        return 'Решка'
    return 'Орел'


def get_chats():
    user_id_set = set()
    with open('txt/ids.txt', 'r', encoding='utf-8') as file:
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
    if 'tiktok' in msg.lower():
        if get_ticktok_nickname(msg) == 'holodova0':
            return TT_KEY
        return 'tiktok'
    random_ans = set()
    if msg not in answers:
        msg_list = msg.split(' ')
        for i in msg_list:
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
    d = seconds // 3600 // 24
    h = seconds // 3600 % 24
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    words_int = [d, h, m, s]
    words_str = ['d', 'h', 'm', 's']
    for i in range(len(words_int)):
        return_string += get_time_str(words_int[i], words_str[i])
    return return_string


def get_weather_today():
    if os.path.exists(f'{"sessions/"}cookies_yandex_weather.pickle'):
        with open(f'{"sessions/"}cookies_yandex_weather.pickle', 'rb') as handle:
            cookies = pickle.load(handle)

    headers = {'X-Yandex-API-Key': YANDEX_API_KEY}

    params = {
        'lat': '43.11981',
        'lon': '131.88692',
        'limit': '1',
        'hours': 'false',
        'extra': 'false'}

    url = 'https://api.weather.yandex.ru/v2/forecast?'
    res = requests.get(url=url, headers=headers, params=params, cookies=cookies)
    try:
        res_in_json = res.json()
    except json.decoder.JSONDecodeError:
        return get_weather_pyowm()

    temp = res_in_json['fact']['temp']
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

    condition = condition_dict[res_in_json['fact']['condition']]

    with open(f'{"sessions/"}cookies_yandex_weather.pickle', 'wb') as handle:
        pickle.dump(res.cookies, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return f'В городе Владивосток {temp}°C, {condition}'


def get_weather_tomorrow():
    if os.path.exists(f'{"sessions/"}cookies_yandex_weather.pickle'):
        with open(f'{"sessions/"}cookies_yandex_weather.pickle', 'rb') as handle:
            cookies = pickle.load(handle)
    string = ""
    headers = {'X-Yandex-API-Key': YANDEX_API_KEY}
    params = {
        'lat': '43.11981',
        'lon': '131.88692',
        'lang': 'ru_RU',
        'limit': '2',
        'extra': 'true'}

    url = 'https://api.weather.yandex.ru/v2/forecast?'
    res = requests.get(url=url, headers=headers, params=params, cookies=cookies)
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
    res_in_json = res.json()
    date = res_in_json['forecasts'][1]['date']
    date_list = date.split('-')
    for i in days_dict:
        temp = res_in_json['forecasts'][1]['parts'][i]['temp_avg']
        condition = condition_dict[res_in_json['forecasts'][1]['parts'][i]['condition']]
        string += f'{days_dict[i]} - средняя температура {temp}°C, {condition}\n'
    with open(f'{"sessions/"}cookies_yandex_weather.pickle', 'wb') as handle:
        pickle.dump(res.cookies, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return f'Завтра ({date_list[2]}.{date_list[1]}.{date_list[0]}) в городе Владивосток\n{string}'


def get_help_message():
    string = ''
    with open('txt/help.txt', 'r', encoding='utf-8') as help_txt:
        for line in help_txt:
            string += line.strip()
            string += '\n'
    return string


def get_btc_price():
    url = 'https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC'
    req = requests.get(url)
    data = json.loads(req.text)
    price = data['result']['Ask']

    return '1 BTC = {0:,} $'.format(int(price))


def get_weather_pyowm():
    config = get_default_config()
    config['language'] = 'ru'

    owm = pyowm.OWM(PYOWM_KEY, config)

    w = owm.weather_manager().weather_at_place('Vladivostok').weather

    temp_c = int(w.temperature('celsius')['temp'])

    return f'В городе Владивосток {temp_c}°C, {w.detailed_status}'


def translate(message: str) -> str:
    translator = Translator(from_lang='ru', to_lang='eng')
    return translator.translate(message)



