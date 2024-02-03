from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from bank.base.model import Transaction, Balance


class BaseBank(metaclass=ABCMeta):
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
    def get_balance(self, account_number: int) -> Balance:
        raise NotImplementedError()

    @abstractmethod
    def get_transaction_history(self, account_number: int) -> list[Transaction]:
        raise NotImplementedError()
