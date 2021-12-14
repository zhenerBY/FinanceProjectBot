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


@bot.message_handler(commands=['balance'])
def send_welcome(message):
    get_balance_pie_chart(user_id=message.chat.id)
    bot.send_message(chat_id=message.chat.id, text=f'{message.chat.first_name}, баланс Ваших расходов и доходов:')
    bot.send_photo(chat_id=message.chat.id, photo=open(f'picts/{message.chat.id}_balance.png', 'rb'))
    os.remove(f'picts/{message.chat.id}_balance.png')


@bot.message_handler(commands=['inc'])
def send_welcome(message):
    get_categories_type_pie_chart(user_id=message.chat.id, cat_type='INC')
    bot.send_message(chat_id=message.chat.id, text=f'{message.chat.first_name}, структура Ваши доходов:')
    bot.send_photo(chat_id=message.chat.id, photo=open(f'picts/{message.chat.id}_categories_type.png', 'rb'))
    os.remove(f'picts/{message.chat.id}_categories_type.png')


@bot.message_handler(commands=['exp'])
def send_welcome(message):
    get_categories_type_pie_chart(user_id=message.chat.id, cat_type='EXP')
    bot.send_message(chat_id=message.chat.id, text=f'{message.chat.first_name}, структура Ваши расходов:')
    bot.send_photo(chat_id=message.chat.id, photo=open(f'picts/{message.chat.id}_categories_type.png', 'rb'))
    os.remove(f'picts/{message.chat.id}_categories_type.png')


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
        'Баланс': 'show_balance',
    }).keyboard
    kb_inc_exp = Keyboa(items=[
        {'Доходы': 'INC'},
        {'Расходы': 'EXP'},
    ], front_marker="&type=", back_marker="$", items_in_row=2).keyboard
    kb_first = Keyboa.combine(keyboards=(kb_balance, kb_inc_exp))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_first,
                          text='Выберите необходимое действие')


@bot.callback_query_handler(func=lambda call: call.data == 'show_balance')
def callback_inline(message):
    chat_id = message.message.chat.id
    first_name = message.message.chat.first_name
    message_id = message.message.id
    kb_menu = Keyboa(items={
        'Вернуться в основное меню': 'main_menu'
    }).keyboard
    get_balance_pie_chart(user_id=chat_id)
    bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_balance.png', 'rb'))
    os.remove(f'picts/{chat_id}_balance.png')
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=f'{first_name}, баланс Ваших расходов и доходов:')
    bot.send_message(chat_id=chat_id, reply_markup=kb_menu, text='Основное меню')


@bot.callback_query_handler(func=lambda call: re.match(r'^&type=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    kb_inc_exp = Keyboa(items=[
        {'Доходы': 'INC'},
        {'Расходы': 'EXP'},
    ], front_marker="&type=", back_marker="$", items_in_row=2).keyboard
    print('Доходы!')
    print(message.data)
    # print(re.search(r''), message.data)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
