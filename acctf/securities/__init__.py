from abc import ABCMeta, abstractmethod

from acctf import Base
from acctf.securities.model import Value


class Securities(Base, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

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
