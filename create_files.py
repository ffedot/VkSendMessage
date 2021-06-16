import os
from requests import get


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


create_files()