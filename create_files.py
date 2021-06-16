import os
from requests import get


def create_files():
    if not os.path.exists('memes'):
        os.mkdir('memes')
    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    if not os.path.exists('logs'):
        os.mkdir('logs')

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

    if not os.path.exists('ids.txt'):
        file = open('ids.txt', 'w')
        file.close()

    if not os.path.exists('polina_answers.txt'):
        file = open('polina_answers.txt', 'w')
        file.close()

    if not os.path.exists('all_answers.txt.txt'):
        file = open('all_answers.txt', 'w')
        file.write('key : word\n')
        file.close()

    if not os.path.exists('.env'):
        file = open('.env', 'w')
        file.write('LOGIN=\n')
        file.write('PASSWORD=\n')
        file.write('PYOWM_KEY=\n')


create_files()