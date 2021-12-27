from dotenv import load_dotenv
import requests
import json

load_dotenv()

HOST_API = 'http://127.0.0.1:8000/api/'
chat_id = 134203883
TOKEN = '994f61ba4bd900112ae616ef66c09fe086576b2e'
APIKEY = 'J8W5JPDw.6zXqClii0tX5pH7e0byYo9bQHjUHuVoz'


# !!!! Edit before deploy!!!!
# HOST_API = os.getenv("HOST_API")
# APIKEY = os.getenv("APIKEY")

# Примеры работы для бота

# С аргументов выводит только текущего пользователя, без - всех
def get_api_users_list(chat_id: int = None) -> list:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    if chat_id is not None:
        data = {
            'chat_id': chat_id,
        }
    else:
        data = {}
    users_data = requests.get(HOST_API + 'apiusers/', json=data, headers=headers)
    json_users_data = users_data.json()
    return json_users_data


# use kwargs name from ApiUserModel. Required 'id' or 'chat_id'
def partial_update_api_users(id: int = None, **kwargs) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    if id is None:
        id = get_api_users_list(chat_id)[0]['id']
    else:
        id = id
    data = {}
    data['id'] = id
    for element in kwargs:
        data[element] = kwargs[element]
    response = requests.patch(HOST_API + 'apiusers/' + str(id) + '/', json=data, headers=headers)
    json_responce = response.json()
    return json_responce


def add_api_users(chat_id, first_name: str = None, last_name: str = None, username: str = None) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'chat_id': chat_id,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
    }
    users_data = requests.post(HOST_API + 'apiusers/', json=data, headers=headers)
    json_users_data = users_data.json()
    json_users_data['status_code'] = users_data.status_code
    return json_users_data


def add_or_update_api_user(chat_id: int, **kwargs) -> dict:
    response = get_api_users_list(chat_id=chat_id)
    if response == []:
        return add_api_users(chat_id, **kwargs)
    update_dict = {}
    for elemet in kwargs:
        if kwargs[elemet] == response[0][elemet]:
            pass
        else:
            update_dict[elemet] = kwargs[elemet]
    if update_dict != {}:
        partial_update_api_users(id=response[0]['id'], **update_dict)
    return response[0]


# С аргументом - только операции пользователя, без - все
# Set the value 'cat_type' 'INC'|'EXP' for separated list
# !!! Do not use at the same time 'cat_type' and 'category'
def get_operations(chat_id: int = None, cat_type: str = None, category: int = None, date_filter_start: str = None,
                   date_filter_end: str = None) -> list:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {}
    if chat_id is not None:
        data['chat_id'] = chat_id
    if cat_type is not None:
        data['cat_type'] = cat_type
    if category is not None:
        data['category'] = category
    if date_filter_start is not None:
        data['date_filter_start'] = date_filter_start
    if date_filter_end is not None:
        data['date_filter_end'] = date_filter_end
    users_data = requests.get(HOST_API + 'operations/', json=data, headers=headers)
    json_users_data = users_data.json()
    return json_users_data


# get detailed information
def get_operation(chat_id: int, id: int) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'chat_id': chat_id,
    }
    users_data = requests.get(HOST_API + 'ext_operations/' + str(id) + '/', json=data, headers=headers)
    json_users_data = users_data.json()
    return json_users_data


# get list of dict {name:id}
def get_list_of_name_operations(chat_id: int, cat_type: str) -> list:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'chat_id': chat_id,
    }
    users_data = requests.get(HOST_API + 'ext_operations/', json=data, headers=headers)
    json_users_data = users_data.json()
    tmp = []
    for item in json_users_data:
        if item['category'][cat_type] == cat_type:
            tmp.append({item['name']: item})
    json_users_data = tmp
    return json_users_data


# создание операции. Если указан chat_id -> user игнорируется
def add_operations(title: str, description: str, amount: float, category: int, user: int = 1,
                   chat_id: int = None) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    if chat_id is not None:
        data = {
            "title": title,
            "description": description,
            "amount": amount,
            "category": category,
            "chat_id": chat_id,
        }
    else:
        data = {
            "title": title,
            "description": description,
            "amount": amount,
            "user": user,
            "category": category,
        }
    response = requests.post(HOST_API + 'operations/', json=data, headers=headers)
    json_responce = response.json()
    return json_responce


# use kwargs name from OperationModel
def partial_update_operations(id: int, **kwargs) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {}
    for element in kwargs:
        data[element] = kwargs[element]
    response = requests.patch(HOST_API + 'operations/' + str(id) + '/', json=data, headers=headers)
    json_responce = response.json()
    return json_responce


# fake operation deletion
def del_operations(id: int) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'id': id,
        'is_active': False
    }
    response = requests.patch(HOST_API + 'operations/' + str(id) + '/', json=data, headers=headers)
    json_responce = response.json()
    return json_responce


# Set the value 'INC'|'EXP' for separated list
def get_categories(cat_type: str = None, chat_id: int = None, unused: bool = None) -> list:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {}
    if chat_id is not None:
        data['chat_id'] = chat_id
    if cat_type is not None:
        data['cat_type'] = cat_type
    if unused is not None:
        if unused is False:
            data['unused'] = False
        else:
            data['unused'] = True
    users_data = requests.get(HOST_API + 'categories/', headers=headers,
                              json=data)
    json_users_data = users_data.json()
    return json_users_data


def add_categories(name: str, cat_type: str, chat_id: int) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'name': name,
        'cat_type': cat_type,
        'chat_id': chat_id,
    }
    users_data = requests.post(HOST_API + 'categories/', json=data, headers=headers)
    json_users_data = users_data.json()
    return json_users_data


def del_categories(id: int) -> int:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    users_data = requests.delete(HOST_API + 'categories/' + str(id) + '/', headers=headers)
    return users_data.status_code


def get_balance(chat_id: int, date_filter_start: str = None, date_filter_end: str = None) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'chat_id': chat_id,
    }
    if date_filter_start is not None:
        data['date_filter_start'] = date_filter_start
    if date_filter_end is not None:
        data['date_filter_end'] = date_filter_end
    users_data = requests.get(HOST_API + 'operations/balance/', headers=headers, json=data)
    json_users_data = users_data.json()
    return json_users_data


def get_categories_balance(chat_id: int, cat_type: str, date_filter_start: str = None,
                           date_filter_end: str = None) -> dict:
    headers = {
        'Authorization': 'Api-Key ' + APIKEY,
    }
    data = {
        'chat_id': chat_id,
        'cat_type': cat_type
    }
    if date_filter_start is not None:
        data['date_filter_start'] = date_filter_start
    if date_filter_end is not None:
        data['date_filter_end'] = date_filter_end
    users_data = requests.get(HOST_API + 'operations/cat_balance/', headers=headers, json=data)
    json_users_data = users_data.json()
    return json_users_data


# # get JWT token. Работает, но пока не используется.
# def get_token(username: str, password: str) -> dict:
#     data = {
#         'username': username,
#         'password': password,
#     }
#     # if is_user_exist(chat_id):
#     #     # return requests.post(HOST_API + 'token/', json=data).json()['access']
#     #     return requests.post(HOST_API + 'token/', json=data).json()
#     # return 'User not registered'
#     return requests.post(HOST_API + 'token/', json=data).json()
#
#
# # Старые примеры. МНогое уже не работает.
#
# # def get_token(chat_id: int) -> str:
# #     data = {
# #         'username': chat_id,
# #         'password': chat_id,
# #     }
# #     if is_user_exist(chat_id):
# #         # return requests.post(HOST_API + 'token/', json=data).json()['access']
# #         return requests.post(HOST_API + 'token/', json=data).json()
# #     return 'User not registered'
#
#
# def get_users_list(chat_id: int) -> list:
#     headers = {
#         'Authorization': 'Bearer ' + get_token(chat_id),
#     }
#     users_data = requests.get(HOST_API + 'users/', headers=headers)
#     json_users_data = users_data.json()
#     return json_users_data
#
#
# def user_registration(chat_id: int) -> None:
#     if not is_user_exist(chat_id):
#         data = {
#             'username': chat_id,
#             'password': chat_id,
#         }
#         requests.post(HOST_API + 'users/register/', json=data)
#
#
# def is_user_exist(chat_id: int) -> bool:
#     data = {
#         'username': chat_id,
#         'password': chat_id,
#     }
#     if requests.post(HOST_API + 'token/', json=data).status_code == 200:
#         return True
#     return False
