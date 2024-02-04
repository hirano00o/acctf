from abc import ABC

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from bank import Bank, Balance, Transaction


class Mizuho(Bank, ABC):
    def __init__(self):
        super().__init__()
        self.driver.get('https://web.ib.mizuhobank.co.jp/servlet/LOGBNK0000000B.do')


    def login(self, user_id: str, password: str):
        user_id_elem = self.driver.find_element(By.NAME, 'txbCustNo')
        user_id_elem.send_keys(user_id)
        self.driver.find_element(By.NAME, 'N00000-next').click()

        user_pw_elem = self.driver.find_element(By.NAME, 'PASSWD_LoginPwdInput')
        user_pw_elem.send_keys(password)
        self.driver.find_element(By.ID, 'btn_login').click()

        try:
            elem = self.driver.find_element(By.XPATH, '//*[@id="button-section"]/a/img')
        except NoSuchElementException as e:
            pass
        else:
            elem.click()

        return self


    def get_balance(self, account_number: int) -> Balance:
        raise NotImplementedError()


    def get_transaction_history(self, account_number: int) -> list[Transaction]:
        raise NotImplementedError()
