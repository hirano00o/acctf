from datetime import date
from enum import Enum


class CurrencyType(Enum):
    jpy = 1
    usd = 2


class DepositType(Enum):
    ordinary = 1  # 普通
    current = 2  # 当座
    fixed = 3  # 定期
    general = 4  # 総合
    savings = 5  # 貯蓄
    hybrid = 6  # SBIハイブリッド預金


def str_to_deposit_type(deposit_type: str) -> DepositType:
    if deposit_type.startswith("普通"):
        return DepositType.ordinary
    elif deposit_type.startswith("当座"):
        return DepositType.current
    elif deposit_type.startswith("定期"):
        return DepositType.fixed
    elif deposit_type.startswith("総合"):
        return DepositType.general
    elif deposit_type.startswith("貯蓄"):
        return DepositType.savings
    elif deposit_type.startswith("ハイブリッド"):
        return DepositType.hybrid

    raise ValueError(f"unspecified deposit type: {deposit_type}")


class Transaction:
    date: date
    content: str
    value: float

    def __init__(self, dt: date, content: str, value: float):
        self.date = dt
        self.content = content
        self.value = value


class Balance:
    account_number: str
    deposit_type: DepositType
    branch_name: str
    value: float

    def __init__(self, account_number: str, deposit_type: DepositType, branch_name: str, value: float):
        self.account_number = account_number
        self.deposit_type = deposit_type
        self.branch_name = branch_name
        self.value = value
