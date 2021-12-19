from dotenv import load_dotenv
import os
import re

import telebot
from telebot import custom_filters, SimpleCustomFilter
from keyboa import Keyboa

from BotAdditional import parser, act_EXP_INC
from bot_matplotlib.matplotlib import get_balance_pie_chart, get_categories_type_pie_chart, get_category_pie_chart
from bot_request.request import get_categories, get_operations, del_operations, get_operation, add_categories, \
    add_operations, partial_update_operations, add_or_update_api_user

load_dotenv()

# !!!! Edit before deploy!!!!
# BOT_TOKEN = os.getenv("BOT_TOKEN")

BOT_TOKEN = '5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM'

# Add Own custom filter
class IsFloatFilter(SimpleCustomFilter):
    key = 'is_float'

    def check(self, message):
        try:
            float(message.text)
        except ValueError:
            return False
        return True


# class for states
class CategoryStates:
    name = 1


# class for states
class OperationStates:
    title = 11
    description = 12
    amount = 13


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_or_update_api_user(chat_id=message.chat.id, first_name=message.chat.first_name,
                           last_name=message.chat.last_name, username=message.chat.username)
    bot.send_message(chat_id=message.chat.id, text=f'Hello {message.chat.first_name}!\n'
                                                   f'Для начала работы введите "/fin"')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text='Незнание - сила!')


@bot.message_handler(commands=['fin'])
def start(message):
    add_or_update_api_user(chat_id=message.chat.id, first_name=message.chat.first_name,
                           last_name=message.chat.last_name, username=message.chat.username)
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
    }, front_marker="&st1=", back_marker="$").keyboard
    kb_inc_exp = Keyboa(items=[
        {'Доходы': 'INC'},
        {'Расходы': 'EXP'},
    ], front_marker="&st1=", back_marker="$", items_in_row=2).keyboard
    kb_first = Keyboa.combine(keyboards=(kb_balance, kb_inc_exp))
    if message.message.text is not None:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_first,
                              text='Выберите необходимое действие')
    else:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id=chat_id, reply_markup=kb_first, text='Выберите необходимое действие')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st1=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = parser(message.data)
    if data[1] in ('INC', 'EXP'):
        act = act_EXP_INC(data[1])
        kb_show = Keyboa(items=[
            {f'📊 Диаграмма {act}ов': f'show_diagram'},
            {f'📄 Просмотреть {act}ы': f'show'},
        ], front_marker="&st2=", back_marker=message.data, items_in_row=2).keyboard
        kb_act = Keyboa(items=[
            {f'➕ Добавить {act}': 'add'},
            {f'❌ Удалить {act}': 'del'},
        ], front_marker="&st2=", back_marker=message.data, items_in_row=2).keyboard
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
    if data[1] == 'show_balance':
        kb_menu = Keyboa(items={
            '⬆ Вернуться в основное меню': 'main_menu'
        }).keyboard
        get_balance_pie_chart(user_id=chat_id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_balance.png', 'rb'), reply_markup=kb_menu,
                       caption=f'{first_name}, баланс Ваших расходов и доходов:')
        os.remove(f'picts/{chat_id}_balance.png')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st2=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = parser(message.data)
    items = []
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад ': '&' + message.data.split('&')[-1]
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    act = act_EXP_INC(data[1])
    if data[2] == 'add':
        categories = get_categories(cat_type=data[1])
        for element in categories:
            items.append({element['name']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&st3=", back_marker=message.data, items_in_row=3).keyboard
        kb_add = Keyboa(items=[{'➕ Добавить категорию': 'newcat'}], front_marker="&st3=", back_marker=message.data,
                        items_in_row=3).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_add, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Выберите категорию')
    elif data[2] == 'del':
        operations = get_operations(chat_id, data[1])
        for element in operations:
            items.append({element['title']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&st3=", back_marker=message.data, items_in_row=2).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Что хотите удалить?')
    elif data[2] == 'show_diagram':
        get_categories_type_pie_chart(user_id=chat_id, cat_type=data[1])
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_categories_type.png', 'rb'),
                       reply_markup=kb_previous,
                       caption=f'{first_name}, диаграмма Ваших {act}ов:')
        os.remove(f'picts/{chat_id}_categories_type.png')
    elif data[2] == 'show':
        kb_show = Keyboa(items=[
            {'Показать все': 'all'},
            {'Показать по категориям': 'cats'},
        ], front_marker="&st3=", back_marker=message.data, items_in_row=2).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_show, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text=f'Выберите необходимый вариант')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st3=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = parser(message.data)
    items = []
    act = act_EXP_INC(data[1])
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st2={data[2]}&st1={data[1]}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    # print(message.data)
    if data[2] == 'show':
        if data[3] == 'all':
            operations = get_operations(chat_id, data[1])
            for element in operations:
                items.append({element['title']: element['id']})
            kb_operations = Keyboa(items=items, front_marker="&st4=op", back_marker=message.data,
                                   items_in_row=2).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_operations, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=f'Выберите {act} для детального отображения.')
        if data[3] == 'cats':
            categories = get_categories(cat_type=data[1], chat_id=chat_id)
            for element in categories:
                items.append({element['name']: element['id']})
            kb_cat = Keyboa(items=items, front_marker="&st4=ct", back_marker=message.data, items_in_row=3).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=f'Выберите категорию.')

    if data[2] == 'add':
        if data[3] == 'newcat':
            bot.set_state(chat_id, CategoryStates.name)
            with bot.retrieve_data(chat_id) as r_data:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                r_data['cat_type'] = data[1]
                r_data['backstep'] = '&' + message.data.split('&', maxsplit=2)[2]
            bot.send_message(chat_id=chat_id, text='Введите название категории\n(для отмены введите "/cancel")')
        elif data[3].isnumeric():
            bot.set_state(chat_id, OperationStates.title)
            with bot.retrieve_data(chat_id) as r_data:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                r_data['category'] = data[3]
                r_data['chat_id'] = chat_id
                r_data['backstep'] = '&' + message.data.split('&', maxsplit=3)[3]
                r_data['operation'] = 'create'
            bot.send_message(chat_id=chat_id, text='Введите название операции\n(для отмены введите "/cancel")')
    if data[2] == 'del':
        del_operations(id=data[3])
        kb_next = Keyboa(items={
            'Продолжить ➡': f'&st2={data[2]}&st1={data[1]}$'
        }).keyboard
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_next,
                              text=f'Операция удалена.')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st4=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = parser(message.data)
    items = []
    act = act_EXP_INC(data[1])
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st3={data[3]}&st2={data[2]}&st1={data[1]}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data[2] == 'show':
        if data[4][:2] == 'op':
            operation = get_operation(chat_id, data[4][2:])
            text = f'Название: {operation["title"]}\nОписание: {operation["description"]}\n' \
                   f'Сумма: {operation["amount"]}\n' \
                   f'Категория: {operation["category"]["name"]}\nСоздано: {operation["created_at"]}'
            kb_edit = Keyboa(items=[{'✏ Редактировать операцию': 'edit'}], front_marker="&st5=",
                             back_marker=message.data).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_edit, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=text)
        if data[4][:2] == 'ct':
            operations = get_operations(chat_id=chat_id, category=data[4][2:])
            for element in operations:
                items.append({element['title']: element['id']})
            kb_operations = Keyboa(items=items, front_marker="&st5=", back_marker=message.data,
                                   items_in_row=2).keyboard
            kb_diag = Keyboa(items=[
                {f'📊 Диаграмма {act}ов по категории': f'diag'},
            ], front_marker="&st5=", back_marker=message.data).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_diag, kb_operations, kb_previous, kb_menu))
            if message.message.text is not None:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                      text=f'Выберите {act} для детального отображения.')
            else:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
                bot.send_message(chat_id=chat_id, reply_markup=kb_all,
                                 text=f'Выберите {act} для детального отображения.')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st5=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = parser(message.data)
    act = act_EXP_INC(data[1])
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st4={data[4]}&st3={data[3]}&st2={data[2]}&st1={data[1]}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data[5] == 'diag':
        get_category_pie_chart(chat_id=chat_id, category=data[4][2:])
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_category.png', 'rb'),
                       reply_markup=kb_previous,
                       caption=f'Диаграмма {act}ов по категории:')
        os.remove(f'picts/{chat_id}_category.png')
    elif data[5].isdigit():
        operation = get_operation(chat_id, data[5])
        text = f'Название: {operation["title"]}\nОписание: {operation["description"]}\n' \
               f'Сумма: {operation["amount"]}\n' \
               f'Категория: {operation["category"]["name"]}\nСоздано: {operation["created_at"]}'
        kb_edit = Keyboa(items=[{'✏ Редактировать операцию': 'edit'}], front_marker="&st6=",
                         back_marker=message.data).keyboard
        kb_all = Keyboa.combine(keyboards=(kb_edit, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                              text=text)
    elif data[5] == 'edit':
        bot.set_state(chat_id, OperationStates.title)
        with bot.retrieve_data(chat_id) as r_data:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            r_data['id'] = data[4][2:]
            r_data['chat_id'] = chat_id
            r_data['backstep'] = '&st4=' + data[4] + '&st3=' + data[3] + \
                                 '&st2=' + data[2] + '&st1=' + data[1] + '$'
            r_data['operation'] = 'change'
        bot.send_message(chat_id=chat_id, text='Введите название операции\n(для отмены введите "/cancel")')
        pass


@bot.callback_query_handler(func=lambda call: re.match(r'^&st6=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    data = parser(message.data)
    if data[6] == 'edit':
        bot.set_state(chat_id, OperationStates.title)
        with bot.retrieve_data(chat_id) as r_data:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            r_data['id'] = data[5]
            r_data['chat_id'] = chat_id
            r_data['category'] = data[4][2:]
            r_data['backstep'] = '&st5=' + data[5] + '&st4=' + data[4] + '&st3=' + data[3] + \
                                 '&st2=' + data[2] + '&st1=' + data[1] + '$'
            r_data['operation'] = 'change'
        bot.send_message(chat_id=chat_id, text='Введите название операции\n(для отмены введите "/cancel")')


# below states handlers
@bot.message_handler(state="*", commands='cancel')
def any_state(message):
    """
    Cancel state
    """
    with bot.retrieve_data(message.from_user.id) as data:
        kb_next = Keyboa(items={
            'Продолжить ➡': data['backstep']
        }).keyboard
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.send_message(message.chat.id, "Ввод отменен", reply_markup=kb_next)
    bot.delete_state(message.from_user.id)


@bot.message_handler(state=CategoryStates.name)
def category_name_get(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['name'] = message.text
        backstep = data['backstep']
        add_categories(name=message.text, cat_type=data['cat_type'])
    kb_next = Keyboa(items={
        'Продолжить ➡': backstep
    }).keyboard
    bot.send_message(chat_id=message.chat.id, text=f'Категория "{message.text}" добавлена.', reply_markup=kb_next)
    bot.delete_state(message.from_user.id)


@bot.message_handler(state=OperationStates.title)
def operation_title_get(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.set_state(message.from_user.id, OperationStates.description)
    with bot.retrieve_data(message.from_user.id) as data:
        data['title'] = message.text
    bot.send_message(chat_id=message.chat.id, text=f'Введите описание\n(для отмены введите "/cancel")')


@bot.message_handler(state=OperationStates.description)
def operation_description_get(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.set_state(message.from_user.id, OperationStates.amount)
    with bot.retrieve_data(message.from_user.id) as data:
        data['description'] = message.text
    bot.send_message(chat_id=message.chat.id, text=f'Введите сумму\n(для отмены введите "/cancel")')


@bot.message_handler(state=OperationStates.amount, is_float=True)
def operation_amount_get(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    with bot.retrieve_data(message.from_user.id) as data:
        data['amount'] = message.text
        backstep = data['backstep']
        if data['operation'] == 'create':
            add_operations(title=data['title'], description=data['description'], amount=data['amount'],
                           category=data['category'], chat_id=data['chat_id'])
        elif data['operation'] == 'change':
            keys = {}
            for element in data:
                if data[element] is not None:
                    keys[element] = data[element]
            partial_update_operations(**keys)
    kb_next = Keyboa(items={
        'Продолжить ➡': backstep
    }).keyboard
    bot.send_message(chat_id=message.chat.id, text=f'Продолжить', reply_markup=kb_next)
    bot.delete_state(message.from_user.id)


@bot.message_handler(state=OperationStates.amount, is_float=False)
def operation_amount_incorrect(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.send_message(message.chat.id, 'Введенное значение не является числом. Повторите ввод.')


# repeater
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    bot.reply_to(message, message.text)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(IsFloatFilter())

# # set saving states into file.
# bot.enable_saving_states()  # you can delete this if you do not need to save states

bot.infinity_polling()
