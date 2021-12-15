import telebot
from keyboa import Keyboa, Button

import re
import os

from request.request import *
from matplotlib_test.examples import *

TOKEN = '5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM'

# used to temporarily store collected information. separately for each user
user_dict = {}


# used to temporarily store collected information
class CategoryCreate():
    def __init__(self, cat_type: str = None, name: str = None, message_id: int = None, backstep: str = None):
        self.cat_type = cat_type
        self.name = name
        self.message_id = message_id
        self.backstep = backstep


# used to temporarily store collected information
class OperationCreate():
    def __init__(self, title: str = None, description: str = None, amount: float = None, category: int = None,
                 chat_id: int = None, message_id: int = None, backstep: str = None):
        self.title = title
        self.description = description
        self.amount = amount
        self.category = category
        self.chat_id = chat_id
        self.message_id = message_id
        self.backstep = backstep


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_api_users(chat_id=message.chat.id, first_name=message.chat.first_name)
    bot.send_message(chat_id=message.chat.id, text=f'Hello {message.chat.first_name}!')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text='Ученье — свет, а неученье — тьма')


@bot.message_handler(commands=['kbd'])
def start(message):
    kb_start = Keyboa(items={
        'Начать работу': 'main_menu',
    }).keyboard
    bot.send_message(chat_id=message.chat.id, reply_markup=kb_start, text=f'{message.chat.first_name}, начнем работу?')


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def kb_start(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    kb_balance = Keyboa(items={
        '📊 Баланс': 'show_balance',
    }, front_marker="&type=", back_marker="$").keyboard
    kb_inc_exp = Keyboa(items=[
        {'Доходы': 'INC'},
        {'Расходы': 'EXP'},
    ], front_marker="&type=", back_marker="$", items_in_row=2).keyboard
    kb_first = Keyboa.combine(keyboards=(kb_balance, kb_inc_exp))
    if message.message.text is not None:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_first,
                              text='Выберите необходимое действие')
    else:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id, reply_markup=kb_first, text='Выберите необходимое действие')


@bot.callback_query_handler(func=lambda call: re.match(r'^&type=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    if data in ('INC', 'EXP'):
        if data == 'INC':
            act = 'доход'
        else:
            act = 'расход'
        kb_show = Keyboa(items=[
            {f'📊 Диаграма {act}ов': f'show_diagram'},
            {f'📄 Просмотреть {act}ы': f'show'},
        ], front_marker="&act=", back_marker=message.data, items_in_row=2).keyboard
        kb_act = Keyboa(items=[
            {f'➕ Добавить {act}': 'add'},
            {f'❌ Удалить {act}': 'del'},
        ], front_marker="&act=", back_marker=message.data, items_in_row=2).keyboard
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_show, kb_act, kb_menu))
        if message.message.text is not None:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                                  text='Выберите следующее действие')
        else:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id=chat_id, reply_markup=kb_second, text='Выберите следующее действие')
    if data == 'show_balance':
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        get_balance_pie_chart(user_id=chat_id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_balance.png', 'rb'), reply_markup=kb_menu,
                       caption=f'{first_name}, баланс Ваших расходов и доходов:')
        os.remove(f'picts/{chat_id}_balance.png')


@bot.callback_query_handler(func=lambda call: re.match(r'^&act=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[1].removeprefix('act=')
    operations = get_operations(chat_id, data)
    categories = get_categories(data)
    items = []
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    if data2 == 'add':
        for element in categories:
            items.append({element['name']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&step3=", back_marker=message.data, items_in_row=3).keyboard
        kb_add = Keyboa(items=[{'➕ Добавить категорию': 'newcat'}], front_marker="&step3=", back_marker=message.data,
                        items_in_row=3).keyboard
        kb_previous = Keyboa(items={
            '⬅ Вернуться на шаг назад ': '&' + message.data.split('&')[-1]
        }).keyboard
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_add, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Выберите категорию')
    elif data2 == 'del':
        for element in operations:
            items.append({element['title']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&step3=", back_marker=message.data, items_in_row=2).keyboard
        kb_previous = Keyboa(items={
            '⬅ Вернуться на шаг назад': '&' + message.data.split('&')[-1]
        }).keyboard
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Что хотите удалить?')
    elif data2 == 'show_diagram':
        kb_menu = Keyboa(items={
            '⬅ Вернуться на шаг назад': '&type=' + data + '$'
        }).keyboard
        get_categories_type_pie_chart(user_id=chat_id, cat_type=data)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_categories_type.png', 'rb'), reply_markup=kb_menu,
                       caption=f'{first_name}, диаграма Ваших {act}ов:')
        os.remove(f'picts/{chat_id}_categories_type.png')
    elif data2 == 'show':
        for element in operations:
            items.append({element['title']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&step3=", back_marker=message.data, items_in_row=2).keyboard
        kb_previous = Keyboa(items={
            '⬅ Вернуться на шаг назад': '&type=' + data + '$'
        }).keyboard
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text=f'Выберите {act} для детального отображения?')


@bot.callback_query_handler(func=lambda call: re.match(r'^&step3=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[2].removeprefix('act=')
    data3 = message.data.split('&')[1].removeprefix('step3=')
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&act={data2}&type={data}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data2 == 'show':
        operation = get_operation(chat_id, data3)
        text = f'Название: {operation["title"]}\nОписание: {operation["description"]}\nСумма: {operation["amount"]}\n' \
               f'Категория: {operation["category"]["name"]}\nСоздано: {operation["created_at"]}'
        kb_edit = Keyboa(items=[{'✏ Редактировать операцию': 'edit'}], front_marker="&step4=",
                         back_marker=message.data).keyboard
        kb_all = Keyboa.combine(keyboards=(kb_edit, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                              text=text)
    if data2 == 'add':
        if data3 == 'newcat':
            msg = bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='Введите название категории')
            user_dict[chat_id] = CategoryCreate(cat_type=data, message_id=message_id,
                                                backstep='&' + message.data.split('&', maxsplit=2)[2])
            bot.register_next_step_handler(msg, process_create_category)
        if data3.isnumeric():
            msg = bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='Введите название операции')
            user_dict[chat_id] = OperationCreate(category=data3, chat_id=chat_id, message_id=message_id,
                                                 backstep='&' + message.data.split('&', maxsplit=3)[3])
            bot.register_next_step_handler(msg, process_create_operation)
            print('current', message_id)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    bot.reply_to(message, message.text)


# below next step handlers
def process_create_category(message):
    chat_id = message.chat.id
    category = user_dict[chat_id]
    category.name = message.text
    bot.delete_message(chat_id=chat_id, message_id=category.message_id)
    add_categories(category.name, category.cat_type)
    kb_next = Keyboa(items={
        'Продолжить ➡': category.backstep
    }).keyboard
    bot.send_message(chat_id=chat_id, text=f'атегория {category.name} добавлена.', reply_markup=kb_next)


def process_create_operation(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    operation.title = message.text
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    print('delete', operation.message_id)
    print('current', message.id)
    operation.message_id = message.id
    msg = bot.send_message(chat_id=chat_id, text='Введите описание операции')
    bot.register_next_step_handler(msg, process_create_operation_2)


def process_create_operation_2(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    operation.description = message.text
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    print('delete', operation.message_id)
    print('current', message.id)
    operation.message_id = message.id
    msg = bot.send_message(chat_id=chat_id, text='Введите сумму операции')
    bot.register_next_step_handler(msg, process_create_operation_3)


def process_create_operation_3(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    print('delete', operation.message_id)
    print('current', message.id)
    try:
        float(message.text)
    except ValueError:

        msg = bot.send_message(chat_id=chat_id, text='Ошибка! Введите число')
        bot.register_next_step_handler(msg, process_create_operation_3)
        operation.message_id = message.id
        return
    pass


bot.infinity_polling()
