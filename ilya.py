import telebot
from telebot import types
import time
from keyboa import Keyboa

bot = telebot.TeleBot('5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM')


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("options")
    item2 = types.KeyboardButton('info')

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Welcome, {0.first_name}!\nI - <b>{1.first_name}</b>, bot created for calculating expenses\n"
                     "Я знаю такие команды, как /option".
                     format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)
    time.sleep(5)


@bot.message_handler(commands=['option'])
def home(message):
    kb_option = Keyboa(
        items=[{"Main menu": 'main_menu'}, ],

    )
    bot.send_message(message.chat.id, text="Select option:", reply_markup=kb_option())


@bot.callback_query_handler(func=lambda x: x.data == 'main_menu')
def option_menu(call):
    kb_option = Keyboa(
        items=[{"expenses": 'exp'}, {"categories": 'cat'}, {"income": 'inc'}, ],
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='select option',
                          reply_markup=kb_option())


@bot.callback_query_handler(func=lambda x: x.data == "exp")
def callback_exp(call):
    option_exp = [{"select category": 'sel_exp'}, {"create new category": 'cr_new_exp'}, {"back": 'back'}, ]
    kb_option_exp = Keyboa(
        items=option_exp,
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='select option',
                          reply_markup=kb_option_exp())


@bot.callback_query_handler(func=lambda x: x.data == "cat")
def callback_cat(call):
    option_cat = [{'show all categories': 'show_all'}, {'show income categories': 'show_inc'},
                  {'show expenses categories':'show_exp'}, {'back': 'back'}]
    kb_option_cat = Keyboa(
        items=option_cat,
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='select option for categories',
                          reply_markup=kb_option_cat())


@bot.callback_query_handler(func=lambda x: x.data == "inc")
def callback_inc(call):
    option_inc = [{'select category': 'sel_inc'}, {'create new category': 'cr_new_inc'}, {'back': 'back'}]
    kb_option_inc = Keyboa(
        items=option_inc,
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='select income',
                          reply_markup=kb_option_inc())


@bot.callback_query_handler(func=lambda x: x.data == 'back')
def callback_back(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    home(call.message)


@bot.callback_query_handler(func=lambda x: x.data == '&exp=select category&option=expenses')
def select_expenses(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


# RUN
bot.polling(none_stop=True)