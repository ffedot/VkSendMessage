from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
import time
from threading import Thread


class YandexBalaboba:

    def __init__(self, message: str):
        self.message = message
        self.texts = []
        self.fill_texts()

    def fill_texts(self):
        threads = []
        for i in range(12):
            t = Thread(target=self.execute_chrome, args=(i, ))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def execute_chrome(self, style):
        url = f'https://yandex.ru/lab/yalm?style={style}'
        user_agent = UserAgent()
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent.Chrome}')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path='driver/chromedriver.exe', options=options)
        driver.get(url=url)
        driver.find_element_by_css_selector('.Button2').click()
        text_input = driver.find_element_by_class_name('Textarea-Control')
        text_input.clear()
        text_input.send_keys(self.message)
        text_input.send_keys(Keys.ENTER)
        try_error = True
        s = 0
        while True:
            if s == 15:
                print("balaboba quit")
                return None
            try:
                output_text = driver.find_element_by_class_name('response__text').text
                driver.close()
                driver.quit()
                self.texts.append(output_text)
                return
            except NoSuchElementException:
                time.sleep(1)
                s += 1
                if try_error:
                    try:
                        error_message = driver.find_element_by_css_selector('.app .init__error_num2')
                        driver.close()
                        driver.quit()
                        return None
                    except NoSuchElementException:
                        try_error = False

    def get_balaboba(self):
        return min(self.texts, key=lambda x: len(x))

