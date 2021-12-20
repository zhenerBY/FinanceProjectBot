from bot_request.request import get_operations

text = '&st6=edit&st5=61&st4=ct16&st3=cats&st2=show&st1=INC$'


# INC show cats ct16 61 edit


def parser(string: str) -> dict:
    output = {}
    pieces = string.split('&')
    pieces_len = len(pieces)
    for num, element in enumerate(range(pieces_len)):
        temp = pieces[num]
        if num == 0:
            pass
        elif num + 1 == pieces_len:
            temp = temp.removesuffix('$')[4:]
            output[pieces_len - num] = temp
        else:
            temp = temp[4:]
            output[pieces_len - num] = temp
    return output


def act_EXP_INC(text: str) -> str:
    if text == 'INC':
        return 'доход'
    else:
        return 'расход'


def check_existence(chat_id:int, cat_type: str = None) -> bool:
    if cat_type is None:
        responseINC = get_operations(chat_id=chat_id, cat_type='INC')
        responseEXP = get_operations(chat_id=chat_id, cat_type='EXP')
        if responseINC == [] or responseEXP == []:
            return False
        return True
    else:
        response = get_operations(chat_id=chat_id, cat_type=cat_type)
        if response == []:
            return False
        return True



# parser(text)
