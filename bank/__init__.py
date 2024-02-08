from datetime import date
from abc import ABCMeta, abstractmethod

from bank.model import Transaction, Balance
from base import Base


class Bank(Base, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_balance(self, account_number: str) -> list[Balance]:
        raise NotImplementedError()

    @abstractmethod
    def get_transaction_history(self, account_number: str, start: date = None, end: date = None) -> list[Transaction]:
        raise NotImplementedError()
