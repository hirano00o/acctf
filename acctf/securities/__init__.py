from abc import ABCMeta, abstractmethod

from selenium import webdriver

from acctf import Base
from acctf.securities.model import Value


class Securities(Base, metaclass=ABCMeta):
    def __init__(self, driver: webdriver = None, timeout: float = 30):
        super().__init__(driver=driver, timeout=timeout)

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
