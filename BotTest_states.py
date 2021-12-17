import os
import re

import telebot
from keyboa import Keyboa
from telebot import custom_filters, SimpleCustomFilter

from matplotlib_test.examples import *
from request.request import *

TOKEN = '5065010726:AAGDDYrw3cQVshBNBSqklLSTjgT2GauBBYM'

# used to temporarily store collected information. separately for each user
user_dict = {}


# Add Own custom filter
class IsFloatFilter(SimpleCustomFilter):
    """
    Filter to check whether the string is made up of only digits.

    Example:
    @bot.message_handler(is_digit=True)
    """
    key = 'is_float'

    def check(self, message):
        try:
            float(message.text)
        except ValueError:
            return False
        return True


# class for states
class CategoryStates:
    cat_type = 1
    name = 2
    message_id = 101
    backstep = 102


# class for states
class OperationStates:
    title = 1
    description = 2
    amount = 3
    category = 4
    chat_id = 5
    id = 6
    message_id = 101
    backstep = 102
    service = 103


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
                 chat_id: int = None, id: int = None, message_id: int = None, backstep: str = None,
                 service: str = 'create'):
        self.title = title
        self.description = description
        self.amount = amount
        self.category = category
        self.chat_id = chat_id
        self.id = id
        self.message_id = message_id
        self.backstep = backstep
        self.service = service


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_api_users(chat_id=message.chat.id, first_name=message.chat.first_name)
    bot.send_message(chat_id=message.chat.id, text=f'Hello {message.chat.first_name}!')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text='Незнание - сила!')


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
    data = message.data.split('=')[-1][:-1]
    if data in ('INC', 'EXP'):
        if data == 'INC':
            act = 'доход'
        else:
            act = 'расход'
        kb_show = Keyboa(items=[
            {f'📊 Диаграма {act}ов': f'show_diagram'},
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
    if data == 'show_balance':
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
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[1].removeprefix('st2=')
    items = []
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад ': '&' + message.data.split('&')[-1]
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    if data2 == 'add':
        categories = get_categories(data)
        for element in categories:
            items.append({element['name']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&st3=", back_marker=message.data, items_in_row=3).keyboard
        kb_add = Keyboa(items=[{'➕ Добавить категорию': 'newcat'}], front_marker="&st3=", back_marker=message.data,
                        items_in_row=3).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_add, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Выберите категорию')
    elif data2 == 'del':
        operations = get_operations(chat_id, data)
        for element in operations:
            items.append({element['title']: element['id']})
        kb_cat = Keyboa(items=items, front_marker="&st3=", back_marker=message.data, items_in_row=2).keyboard
        kb_second = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_second,
                              text='Что хотите удалить?')
    elif data2 == 'show_diagram':
        get_categories_type_pie_chart(user_id=chat_id, cat_type=data)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_categories_type.png', 'rb'),
                       reply_markup=kb_previous,
                       caption=f'{first_name}, диаграма Ваших {act}ов:')
        os.remove(f'picts/{chat_id}_categories_type.png')
    elif data2 == 'show':
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
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[2].removeprefix('st2=')
    data3 = message.data.split('&')[1].removeprefix('st3=')
    items = []
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st2={data2}&st1={data}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    # print(message.data)
    if data2 == 'show':
        if data3 == 'all':
            operations = get_operations(chat_id, data)
            for element in operations:
                items.append({element['title']: element['id']})
            kb_operations = Keyboa(items=items, front_marker="&st4=op", back_marker=message.data,
                                   items_in_row=2).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_operations, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=f'Выберите {act} для детального отображения.')
        if data3 == 'cats':
            categories = get_categories(data)
            for element in categories:
                items.append({element['name']: element['id']})
            kb_cat = Keyboa(items=items, front_marker="&st4=ct", back_marker=message.data, items_in_row=3).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_cat, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=f'Выберите категорию.')

    if data2 == 'add':
        if data3 == 'newcat':
            with bot.retrieve_data(message.from_user.id) as data:
                data['cat_type'] = data
                data['message_id'] = message_id
                data['backstep'] = '&' + message.data.split('&', maxsplit=2)[2]
            bot.set_state(chat_id, CategoryStates.name)
            bot.send_message(message.chat.id, 'Введите название операции\n(для отмены введите "/cancel")')
            # msg = bot.edit_message_text(chat_id=chat_id, message_id=message_id,
            #                             text='Введите название категории')
            # user_dict[chat_id] = CategoryCreate(cat_type=data, message_id=message_id,
            #                                     backstep='&' + message.data.split('&', maxsplit=2)[2])
            # bot.register_next_step_handler(msg, process_create_category)
        elif data3.isnumeric():
            msg = bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='Введите название операции')
            user_dict[chat_id] = OperationCreate(category=data3, chat_id=chat_id, message_id=message_id,
                                                 backstep='&' + message.data.split('&', maxsplit=3)[3])
            bot.register_next_step_handler(msg, process_create_operation)
    if data2 == 'del':
        del_operations(id=data3)
        kb_next = Keyboa(items={
            'Продолжить ➡': f'&st2={data2}&st1={data}$'
        }).keyboard
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_next,
                              text=f'Операция удалена.')


@bot.callback_query_handler(func=lambda call: re.match(r'^&st4=', call.data))
def callback_inline(message):
    chat_id = message.message.chat.id
    message_id = message.message.id
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[3].removeprefix('st2=')
    data3 = message.data.split('&')[2].removeprefix('st3=')
    data4 = message.data.split('&')[1].removeprefix('st4=')
    items = []
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st3={data3}&st2={data2}&st1={data}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data2 == 'show':
        if data4[:2] == 'op':
            operation = get_operation(chat_id, data4[2:])
            text = f'Название: {operation["title"]}\nОписание: {operation["description"]}\n' \
                   f'Сумма: {operation["amount"]}\n' \
                   f'Категория: {operation["category"]["name"]}\nСоздано: {operation["created_at"]}'
            kb_edit = Keyboa(items=[{'✏ Редактировать операцию': 'edit'}], front_marker="&st5=",
                             back_marker=message.data).keyboard
            kb_all = Keyboa.combine(keyboards=(kb_edit, kb_previous, kb_menu))
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                                  text=text)
        if data4[:2] == 'ct':
            operations = get_operations(chat_id=chat_id, category=data4[2:])
            for element in operations:
                items.append({element['title']: element['id']})
            kb_operations = Keyboa(items=items, front_marker="&st5=", back_marker=message.data,
                                   items_in_row=2).keyboard
            kb_diag = Keyboa(items=[
                {f'📊 Диаграма {act}ов по категории': f'diag'},
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
    first_name = message.message.chat.first_name
    data = message.data.split('=')[-1][:-1]
    data2 = message.data.split('&')[4].removeprefix('st2=')
    data3 = message.data.split('&')[3].removeprefix('st3=')
    data4 = message.data.split('&')[2].removeprefix('st4=')
    data5 = message.data.split('&')[1].removeprefix('st5=')
    print(message.data, data, data2, data3, data4, data5)
    items = []
    if data == 'INC':
        act = 'доход'
    else:
        act = 'расход'
    kb_previous = Keyboa(items={
        '⬅ Вернуться на шаг назад': f'&st4={data4}&st3={data3}&st2={data2}&st1={data}$'
    }).keyboard
    kb_menu = Keyboa(items={
        '⬆ Вернуться в основное меню': 'main_menu'
    }).keyboard
    if data5 == 'diag':
        get_category_pie_chart(chat_id=chat_id, category=data4[2:])
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=open(f'picts/{chat_id}_category.png', 'rb'),
                       reply_markup=kb_previous,
                       caption=f'Диаграма {act}ов по категории:')
        os.remove(f'picts/{chat_id}_category.png')
    elif data5.isdigit():
        operation = get_operation(chat_id, data5)
        text = f'Название: {operation["title"]}\nОписание: {operation["description"]}\n' \
               f'Сумма: {operation["amount"]}\n' \
               f'Категория: {operation["category"]["name"]}\nСоздано: {operation["created_at"]}'
        kb_edit = Keyboa(items=[{'✏ Редактировать операцию': 'edit'}], front_marker="&st6=",
                         back_marker=message.data).keyboard
        kb_all = Keyboa.combine(keyboards=(kb_edit, kb_previous, kb_menu))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=kb_all,
                              text=text)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(message.text)
    bot.reply_to(message, message.text)


# below states handlers
@bot.message_handler(state="*", commands='cancel')
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Ввод отменен")
    bot.delete_state(message.from_user.id)


@bot.message_handler(state=CategoryStates.name)
def category_name_get(message):
    with bot.retrieve_data(message.from_user.id) as data:
        bot.delete_message(data['message_id'])
        data['name'] = message.text
        data['message_id'] = message.chat.id
        backstep = data['backstep']
    kb_next = Keyboa(items={
        'Продолжить ➡': backstep
    }).keyboard
    bot.send_message(chat_id=message.chat.id, text=f'Категория "{message.text}" добавлена.', reply_markup=kb_next)
    print(bot.retrieve_data(message.from_user.id).__dict__)
    bot.delete_state(message.from_user.id)


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
    bot.send_message(chat_id=chat_id, text=f'Категория {category.name} добавлена.', reply_markup=kb_next)


def process_create_operation(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    operation.title = message.text
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    msg = bot.send_message(chat_id=chat_id, text='Введите описание операции')
    operation.message_id = msg.message_id
    bot.register_next_step_handler(msg, process_create_operation_2)


def process_create_operation_2(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    operation.description = message.text
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    msg = bot.send_message(chat_id=chat_id, text='Введите сумму операции')
    operation.message_id = msg.message_id
    bot.register_next_step_handler(msg, process_create_operation_3)


def process_create_operation_3(message):
    chat_id = message.chat.id
    operation = user_dict[chat_id]
    bot.delete_message(chat_id=chat_id, message_id=operation.message_id)
    try:
        float(message.text)
    except ValueError:
        msg = bot.send_message(chat_id=chat_id, text='Ошибка! Введите число')
        bot.register_next_step_handler(msg, process_create_operation_3)
        operation.message_id = msg.message_id
        return
    pass
    operation.amount = message.text
    kb_next = Keyboa(items={
        'Продолжить ➡': operation.backstep
    }).keyboard
    if operation.service == 'create':
        add_operations(title=operation.title, description=operation.description, amount=operation.amount,
                       category=operation.category, chat_id=operation.chat_id)
        bot.send_message(chat_id=chat_id, text=f'Операция {operation.title} добавлена.', reply_markup=kb_next)
    elif operation.service == 'update':
        partial_update_operations(id=operation.id, title=operation.title, description=operation.description,
                                  amount=operation.amount,
                                  category=operation.category, chat_id=operation.chat_id)
        bot.send_message(chat_id=chat_id, text=f'Операция изменена.', reply_markup=kb_next)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(IsFloatFilter())

bot.infinity_polling()
