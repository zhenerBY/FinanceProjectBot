import telebot

TOKEN = '5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    import pdb
    pdb.set_trace()
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
