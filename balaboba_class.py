import json
import urllib.request
from threading import Thread
from fake_useragent import UserAgent


class YandexBalaboba:

    def __init__(self, message: str):
        self.message = message
        self.texts = []
        self.fill_texts()

    def fill_texts(self):
        threads = []
        for i in range(12):
            t = Thread(target=self.get_response, args=(i, ))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def get_response(self, style):
        api_url = 'https://zeapi.yandex.net/lab/api/yalm/text3'
        user_agent = UserAgent()
        headers = {
            'Content-Type': 'application/json',
            "User-Agent": user_agent.Chrome,
            'Origin': 'https://yandex.ru',
            'Referer': 'https://yandex.ru/',
        }
        payload = {"query": self.message, "intro": 0, "filter": style}
        params = json.dumps(payload).encode('UTF-8')
        req = urllib.request.Request(api_url, data=params, headers=headers)
        response = urllib.request.urlopen(req)
        res = response.read()
        text = json.loads(res)['text']
        self.texts.append(text)

    def get_balaboba(self):
        return min(self.texts, key=lambda x: len(x))

