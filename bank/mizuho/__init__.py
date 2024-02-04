from abc import ABC
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from bank import Bank, Balance, Transaction
from bank.model import str_to_deposit_type


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
        self.driver.find_element(By.ID, 'MB_R011N030').click()
        # When there is the account select box
        try:
            elem = self.driver.find_element(By.CLASS_NAME, 'n03000-t1')
            tr = iter(elem.find_elements(By.TAG_NAME, "tr"))
            # skip header
            next(tr)
            for num, t in enumerate(tr):
                if t.find_elements(By.TAG_NAME, "span")[2].text == str(account_number):
                    t.find_element(By.NAME, f"chkAccChkBx_{str(num).zfill(3)}").click()
                    break
            self.driver.find_element(By.XPATH, '//*[@id="main"]/section/input').click()
        except NoSuchElementException as e:
            pass

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table")

        df = pd.read_html(StringIO(str(table)))[0]
        df = df.iloc[:,-1]

        return Balance(
            account_number=account_number,
            deposit_type=str_to_deposit_type(df[1]),
            branch_name=df[0],
            value = float(df[3].replace(",", "").replace("円", ""))
        )


    def get_transaction_history(self, account_number: int) -> list[Transaction]:
        raise NotImplementedError()
