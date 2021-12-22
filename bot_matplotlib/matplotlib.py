import numpy as np
import matplotlib.pyplot as plt

from bot_request.request import get_balance, get_categories_balance, get_operations

CHAT_ID = 11111111


# function for pie_autopct
def func(pct, allvals):
    absolute = int(np.round(pct / 100. * np.sum(allvals)))
    return "{:.1f}\n({:.1f}%)".format(absolute, pct)


def get_balance_pie_chart(user_id: int):
    balance = get_balance(user_id)
    labels = 'Income', 'Expenses'
    sizes = [balance['balance']['inc'], balance['balance']['exp']]
    explode = (0.05, 0.05)  # only "explode" the 2nd slice (i.e. 'Hogs')
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizes),
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # safe file
    plt.savefig(f'picts/{user_id}_balance.png', transparent=True)
    # plt.show()
    plt.close('all')


def get_categories_type_pie_chart(user_id: int, cat_type: str):
    balance = get_categories_balance(user_id, cat_type)
    labels = []
    sizes = []
    explode = []
    for element in balance['categories']:
        labels.append(element)
        sizes.append(balance['categories'][element])
        explode.append(0.05)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizes),
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # safe file
    plt.savefig(f'picts/{user_id}_categories_type.png', transparent=True)
    # plt.show()
    plt.close('all')


def get_category_pie_chart(chat_id: int, category: int):
    operations = get_operations(chat_id=chat_id, category=category)
    labels = []
    sizes = []
    explode = []
    for element in operations:
        labels.append(element['title'])
        sizes.append(element['amount'])
        explode.append(0.05)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct=lambda pct: func(pct, sizes),
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # safe file
    plt.savefig(f'picts/{chat_id}_category.png', transparent=True)
    # plt.show()
    plt.close('all')
