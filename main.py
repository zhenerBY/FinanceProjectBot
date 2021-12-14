import telebot
from telebot import types

bot = telebot.TeleBot('5024571843:AAEGODz_k7S5ZDGkOQ3iqfg2Mb_aVv7-56c')


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


@bot.message_handler(commands=['option'])
def option(message):
    if message.chat.type == 'private':
        if message.text == '/option':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("expenses", callback_data='exp')
            item2 = types.InlineKeyboardButton("categories", callback_data='cat')
            item3 = types.InlineKeyboardButton("income", callback_data='inc')
            markup.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'select option', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Value ERROR')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'exp':
                markup = types.InlineKeyboardMarkup(row_width=2)

                item1 = types.InlineKeyboardButton("select category", callback_data='select')
                item2 = types.InlineKeyboardButton("create new category and save expenses", callback_data='cr+sv')
                item3 = types.InlineKeyboardButton("back", callback_data='back')
                markup.add(item1, item2, item3)

                msg = bot.send_message(call.message.chat.id, 'select option', reply_markup=markup)
                bot.register_next_step_handler(msg, callback_expenses)
            elif call.data == 'cat':
                markup = types.InlineKeyboardMarkup(row_width=2)

                item1 = types.InlineKeyboardButton("show category", callback_data='show')
                item2 = types.InlineKeyboardButton("create new category", callback_data='cr')
                item3 = types.InlineKeyboardButton("back", callback_data='back')
                markup.add(item1, item2, item3)

                bot.send_message(call.message.chat.id, 'select option', reply_markup=markup)
            elif call.data == 'inc':
                markup = types.InlineKeyboardMarkup(row_width=2)

                item1 = types.InlineKeyboardButton("new income", callback_data='n_i')
                item2 = types.InlineKeyboardButton("back", callback_data='back')
                markup.add(item1, item2)

                bot.send_message(call.message.chat.id, 'select option', reply_markup=markup)

    except Exception as e:
        print(repr(e))



def callback_expenses(call):
    if call.data == 'show':
        pass
    elif call.data == 'cr':
        pass
    elif call.data == 'back':
        bot.send_message(call.message.chat.id, 'ex')

@bot.callback_query_handler(func=lambda call: True)
def callback_category(call):
    if callback_inline.data == 'select':
        pass
    elif callback_inline.data == 'cr+sv':
        pass
    elif callback_inline.data == 'back':
        bot.send_message(call.message.chat.id, 'cat')


@bot.callback_query_handler(func=lambda call: True)
def callback_income(call):
    if callback_inline.data == 'n_i':
        pass
    elif callback_inline.data == 'back':
        bot.send_message(call.message.chat.id, 'in')

# RUN
bot.polling(none_stop=True)