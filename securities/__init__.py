from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from securities.model import Value


class Securities(metaclass=ABCMeta):
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
