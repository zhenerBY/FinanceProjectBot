import telebot
from keyboa import Keyboa, Button

import re
import os

from request.request import *
from matplotlib_test.examples import *

TOKEN = '5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM'

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
    }).keyboard
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


@bot.callback_query_handler(func=lambda call: call.data == 'show_balance')
def callback_inline(message):
    chat_id = message.message.chat.id
    first_name = message.message.chat.first_name
    message_id = message.message.id
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    get_balance_pie_chart(user_id=chat_id)
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_balance.png', 'rb'), reply_markup=kb_menu,
                   caption=f'{first_name}, баланс Ваших расходов и доходов:')
    os.remove(f'picts/{chat_id}_balance.png')


@bot.callback_query_handler(func=lambda call: re.match(r'^&type=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = message.data.split('=')[-1][:-1]
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    kb_show = Keyboa(items=[
        {f'📊 Диаграма {act}ов': f'show_diagram_{data}'},
        {f'📄 Просмотреть {act}ы': f'show_detail_{data}'},
    ], items_in_row=2).keyboard
    kb_act = Keyboa(items=[
        {f'➕ Добавить {act}': 'add'},
        {f'❌ Удалить {act}': 'del'},
    ], front_marker="&act=", back_marker=message.data, items_in_row=2).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    kb_second = Keyboa.combine(keyboards=(kb_show, kb_act, kb_menu))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                          text='Выберите следующее действие')


@bot.callback_query_handler(func=lambda call: re.match(r'^&act=add', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = message.data.split('=')[-1][:-1]
    categories = get_categories(data)
    items = []
    for element in categories:
        items.append({element['name']: element['id']})
    kb_cat = Keyboa(items=items, front_marker="&id=", back_marker=message.data, items_in_row=3).keyboard
    kb_add = Keyboa(items=[{'➕ Добавить категорию': 'addcat'}], front_marker="&addcat=", back_marker=message.data,
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


@bot.callback_query_handler(func=lambda call: re.match(r'^&act=del', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = message.data.split('=')[-1][:-1]
    categories = get_operations(chat_id, data)
    items = []
    for element in categories:
        items.append({element['title']: element['id']})
    kb_cat = Keyboa(items=items, front_marker="&id=", back_marker=message.data, items_in_row=2).keyboard
    kb_add = Keyboa(items=[{'➕ Добавить категорию': 'addcat'}], front_marker="&addcat=", back_marker=message.data,
                    items_in_row=3).keyboard
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': '&' + message.data.split('&')[-1]
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    kb_second = Keyboa.combine(keyboards=(kb_cat, kb_add, kb_previous, kb_menu))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                          text='Что хотите удалить?')


@bot.callback_query_handler(func=lambda call: re.match(r'^show_diagram', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    first_name = message.message.chat.first_name
    message_id = message.message.id
    data = message.data.split('_')[-1]
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    get_categories_type_pie_chart(user_id=chat_id, cat_type=data)
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_categories_type.png', 'rb'), reply_markup=kb_menu,
                   caption=f'{first_name}, диаграма Ваших {act}ов:')
    os.remove(f'picts/{chat_id}_categories_type.png')


@bot.callback_query_handler(func=lambda call: re.match(r'^show_detail_', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = message.data.split('_')[-1]
    operations = get_operations(chat_id, data)
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    items = []
    for element in operations:
        items.append({element['title']: element['id']})
    kb_cat = Keyboa(items=items, front_marker="&id=", back_marker=message.data, items_in_row=2).keyboard
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': '&type=' + data + '$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    kb_second = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                          text=f'Выберите {act} для детального отображения?')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    bot.reply_to(message, message.text)


bot.infinity_polling()
