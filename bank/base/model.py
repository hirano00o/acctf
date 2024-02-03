from datetime import date
from enum import Enum


class DepositType(Enum):
    ordinary = 1  # 普通
    current = 2  # 当座
    fixed = 3  # 定期
    general = 4  # 総合
    savings = 5  # 貯蓄


class Transaction:
    date: date
    content: str
    value: float

    def __init__(self, dt: date, content: str, value: float):
        self.date = dt
        self.content = content
        self.value = value


class Balance:
    account_number: int
    deposit_type: DepositType
    branch_name: str
    value: float

    def __init__(self, account_number: int, deposit_type: DepositType, branch_name: str, value: float):
        self.account_number = account_number
        self.deposit_type = deposit_type
        self.branch_name = branch_name
        self.value = value
