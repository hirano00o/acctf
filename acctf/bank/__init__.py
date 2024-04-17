from datetime import date
from abc import ABCMeta, abstractmethod

from selenium import webdriver

from acctf.bank.model import Transaction, Balance, CurrencyType
from acctf import Base


class Bank(Base, metaclass=ABCMeta):
    def __init__(self, driver: webdriver = None, timeout: float = 30):
        super().__init__(driver=driver, timeout=timeout)

    @abstractmethod
    def get_balance(self, account_number: str) -> list[Balance]:
        raise NotImplementedError()

    @abstractmethod
    def get_transaction_history(
        self,
        account_number: str,
        start: date = None,
        end: date = None,
        currency: CurrencyType = None,
    ) -> list[Transaction]:
        raise NotImplementedError()
