from abc import ABCMeta, abstractmethod
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


class Value:
    name: str
    amount: float
    acquisition_value: float
    current_value: float

    def __init__(self, name: str, amount: float, acquisition_value: float, current_value: float):
        self.name = name
        self.amount = amount
        self.acquisition_value = acquisition_value
        self.current_value = current_value


class BaseSecurities(metaclass=ABCMeta):
    driver: WebDriver

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    @abstractmethod
    def login(self, user_id: str, password: str):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()

    @abstractmethod
    def get_stock_specific(self) -> List[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_specific(self) -> List[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_nisa_accum(self) -> List[Value]:
        raise NotImplementedError()

    @abstractmethod
    def get_fund_old_nisa_accum(self) -> List[Value]:
        raise NotImplementedError()

    @abstractmethod
    def concat(self):
        raise NotImplementedError()
