import time
from abc import ABC
from datetime import date
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from bank import Bank, Balance, Transaction
from bank.model import str_to_deposit_type


class SBI(Bank, ABC):
    account_number = ""
    branch_name = ""

    def __init__(self):
        super().__init__()
        self.driver.get('https://www.netbk.co.jp/contents/pages/wpl010101/i010101CT/DI01010210')


    def login(self, user_id: str, password: str, otp: str | None = None):
        user_id_elem = self.driver.find_element(By.ID, 'userNameNewLogin')
        user_id_elem.send_keys(user_id)

        user_pw_elem = self.driver.find_element(By.ID, 'loginPwdSet')
        user_pw_elem.send_keys(password)
        self.driver.find_element(By.TAG_NAME, 'button').click()
        time.sleep(5)
        self.driver.set_window_size(1024, 600)
        self._get_account_info()

        return self


    def get_balance(self, account_number: str) -> list[Balance]:
        if account_number != "" and account_number is not None:
            self.account_number = account_number

        self.driver.find_element(By.CLASS_NAME, 'm-icon-ps_balance').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table")

        df = pd.read_html(StringIO(str(table)))
        ret = []
        for d in df:
            if d.columns[-1] == "取引メニュー" and d.columns[-2] != "円換算額":
                dtype = str_to_deposit_type("普通")
                if d.columns[0] != "口座":
                    dtype = str_to_deposit_type("ハイブリッド")
                ret.append(
                    Balance(
                        account_number=self.account_number,
                        deposit_type=dtype,
                        branch_name=self.branch_name,
                        value = float(d["残高"][0].replace(",", "").replace("円", ""))
                    )
                )

        return ret


    def get_transaction_history(self, account_number: str, start: date = None, end: date = None) -> list[Transaction]:
        """Gets the transaction history. If start or end parameter is empty, return the history of current month.

        :param account_number: specify an account number.
        :param start: start date of transaction history. After the 1st of the month before the previous month.
        :param end: end date of transaction history. Until today.
        """
        if account_number != "" and account_number is not None:
            self.account_number = account_number

        return []

    def _get_account_info(self):
        self.branch_name = self.driver.find_element(
            By.XPATH,
            '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[1]').text

        self.account_number= self.driver.find_element(
            By.XPATH,
            '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[3]').text
