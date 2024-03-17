import re


def format_displayed_money(v: str) -> str:
    return re.sub(r'[A-Za-z円,¥￥\s]+', "", v)
