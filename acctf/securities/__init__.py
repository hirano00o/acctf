from abc import ABCMeta, abstractmethod

from playwright.sync_api import Page

from acctf import Base
from acctf.securities.model import Value


class Securities(Base, metaclass=ABCMeta):
    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)

    @abstractmethod
    def get_stock_specific(self) -> list[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_stock_specific_us(self) -> list[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_specific(self) -> list[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_nisa_accum(self) -> list[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_old_nisa_accum(self) -> list[Value]:
        raise NotImplementedError()
