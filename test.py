from datetime import date, datetime


def period_filter(text: str) -> bool:
    try:
        text_date = datetime.strptime(text, '%d-%m-%Y').date()
    except Exception:
        return False
    if datetime.now().date() < text_date:
        return False
    return True