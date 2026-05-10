from datetime import date
from abc import ABCMeta, abstractmethod

from playwright.sync_api import Page

from acctf.bank.model import Transaction, Balance, CurrencyType
from acctf import Base


class Bank(Base, metaclass=ABCMeta):
    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)

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
