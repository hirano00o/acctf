from enum import Enum

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
