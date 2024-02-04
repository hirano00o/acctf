from abc import ABCMeta, abstractmethod

from bank.model import Transaction, Balance
from base import Base


class Bank(Base, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def login(self, user_id: str, password: str):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()

    @abstractmethod
    def get_balance(self, account_number: str) -> Balance:
        raise NotImplementedError()

    @abstractmethod
    def get_transaction_history(self, account_number: str) -> list[Transaction]:
        raise NotImplementedError()
