from vk_messages import MessagesAPI
from vk_messages.utils import get_random
from settings import LOGIN, PASSWORD
import vk_api


messages = MessagesAPI(login=LOGIN, password=PASSWORD, two_factor=False)
vk_session = vk_api.VkApi(LOGIN, PASSWORD)
vk_session.auth()
print("Вход выполнен")

vk = vk_session.get_api()


from_id = vk.users.get(name_case='gen')[0]['id']

print('Вводите ID пользователей, для прекращения ввода введите 0')
user_id = input()
user_id_set = set()
user_id_list = list()
while user_id != '0':
    user_id_set.add(user_id)
    user_id = input()

message_to_search = input("Введите сообщение на которое будем отвечать:\n").lower()
message_to_send = input("Введите сообщение которое будем отправлять:\n")


for user in user_id_set:
    temp_history = messages.method('messages.getHistory', user_id=user, count=1)
    try:
        get_msg = temp_history['items'][0]['text']
    except IndexError:
        print(f'Диалог с пользователем {user} не найден, пользователь удален из списка')
        continue
    user_id_list.append(user)

for user in user_id_list:
    first_name = vk.users.get(name_case='gen', user_ids=user)[0]['first_name']
    last_name = vk.users.get(name_case='gen', user_ids=user)[0]['last_name']
    print(f'Бот активирован для {first_name} {last_name}')

while True:
    for user_id in user_id_list:
        history = messages.method('messages.getHistory', user_id=user_id, count=1)
        last_msg_text = history['items'][0]['text']
        last_msg_id = history['items'][0]['from_id']
        if last_msg_id != from_id:
            if last_msg_text == message_to_search:
                messages.method('messages.send', user_id=user_id, message=message_to_send, random_id=get_random())
                print(f'Отправлено сообщение "{message_to_send}" пользователю с ID {user_id}')
