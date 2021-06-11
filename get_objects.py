from bs4 import BeautifulSoup
from requests import get, exceptions


def get_ticktok_nickname(url: str):
    headers = {
        'Accept': '*/*',
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 YaBrowser/21.5.2.638 Yowser/2.5 Safari/537.36'
    }
    try:
        req = get(url, headers=headers)
    except exceptions.MissingSchema:
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


def get_answers():
    answers = dict()
    with open('answers.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if line[0].strip() == '#':
                continue
            s = line.strip().split(':')
            answers[s[0][:-1]] = s[1][1:]
    return answers


def get_chats():
    user_id_set = set()
    with open('id.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if line[0].strip() == '#':
                continue
            user_id_set.add(line.strip())
    return user_id_set
