import telebot
from keyboa import Keyboa

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
    bot.reply_to(message, "Howdy, how are you doing?")


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
def send_welcome(message):
    fruits_with_ids = [
        {"banana": "101"}, {"coconut": "102"}, {"orange": "103"},
        {"peach": "104"}, {"apricot": "105"}, {"apple": "106"},
        {"pineapple": "107"}, {"avocado": "108"}, {"melon": "109"},
    ]
    kb_fruits = Keyboa(items=fruits_with_ids, items_in_row=3)
    bot.send_message(chat_id=message.chat.id, reply_markup=kb_fruits(), text='Please select one of the fruit:')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
