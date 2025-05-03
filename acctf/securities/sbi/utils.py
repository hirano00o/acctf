from enum import Enum

from bs4 import PageElement

from acctf.securities.model import Value
import pandas as pd


class AccountType(Enum):
    jp = 1
    us = 2


def get_formatted(df: pd.DataFrame, account_type: AccountType) -> list[Value]:
    if df is None:
        return []
    if account_type == AccountType.jp:
        df = df.drop(df.index[0])
    df = df.iloc[:,0:3]
    code_df = df[::2].iloc[:,[1]].reset_index(drop=True).set_axis(['name'], axis=1)
    val_df = df[1::2].reset_index(drop=True).set_axis(['amount', 'acquisition_val', 'current_val'], axis=1)
    ret: list[Value] = []
    for _, row in pd.concat([code_df, val_df], axis=1).iterrows():
        ret.append(Value(row['name'], row['amount'], row['acquisition_val'], row['current_val']))

    return ret

def get_formatted_for_ul_tables(pe: PageElement) -> list[Value]:
    if pe is None:
        return []
    ret: list[Value] = []
    for i, li in enumerate(pe.find_all_next("li", class_="table-row bd-0 table-primary-row")):
        if i == 0:
            continue
        titles = li.find_next("div", class_="security-title-item css-kat7it")
        if titles is None or len(titles) < 2:
            continue
        code = titles.contents[0].getText().strip()
        name = titles.contents[1].getText().strip()
        full_stock_name = " ".join([code, name])

        class_name = "security-amount-item flex flex-middle flex-right text-right css-sfy3gr"
        amount = (li.find_next("label", class_=class_name).
                  getText().strip())
        acquisition_value_tag = li.find_next("div", class_=class_name)
        acquisition_value = acquisition_value_tag.getText().strip()
        current_value = acquisition_value_tag.find_next("div", class_=class_name).getText().strip()

        ret.append(Value(full_stock_name, float(amount), float(acquisition_value), float(current_value)))

    return ret
