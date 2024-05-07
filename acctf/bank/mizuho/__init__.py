from abc import ABC
from datetime import date, datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from acctf.bank import Bank, Balance, Transaction
from acctf.bank.model import str_to_deposit_type, CurrencyType


class Mizuho(Bank, ABC):
    def __init__(self, driver: webdriver = None, timeout: float = 30):
        super().__init__(driver=driver, timeout=timeout)
        self.driver.get('https://web.ib.mizuhobank.co.jp/servlet/LOGBNK0000000B.do')


    def login(self, user_id: str, password: str, totp: str | None = None):
        user_id_elem = self.find_element(By.NAME, 'txbCustNo')
        user_id_elem.send_keys(user_id)
        self.driver.find_element(By.NAME, 'N00000-next').click()

        user_pw_elem = self.find_element(By.NAME, 'PASSWD_LoginPwdInput')
        user_pw_elem.send_keys(password)
        self.driver.find_element(By.ID, 'btn_login').click()

        try:
            important_notification = '//*[@id="button-section"]/a/img'
            elem = self.find_element(By.XPATH, important_notification)
        except TimeoutException:
            pass
        else:
            elem.click()

        return self


    def logout(self):
        self.driver.find_element(By.XPATH, '//*[@id="side-menu"]/div[1]/a/img').click()


    def get_balance(self, account_number: str) -> list[Balance]:
        balance = 'MB_R011N030'
        elem = self.find_element_to_be_clickable(By.ID, balance)
        elem.click()
        # When there is the account select box
        try:
            select = 'n03000-t1'
            elem = self.find_element(By.CLASS_NAME, select)
            tr = iter(elem.find_elements(By.TAG_NAME, "tr"))
            # skip header
            next(tr)
            for num, t in enumerate(tr):
                if t.find_elements(By.TAG_NAME, "span")[2].text == account_number:
                    t.find_element(By.NAME, f"chkAccChkBx_{str(num).zfill(3)}").click()
                    break
            self.driver.find_element(By.XPATH, '//*[@id="main"]/section/input').click()
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table")
        if table is None or len(table) == 0:
            return []

        df = pd.read_html(StringIO(str(table)))[0]
        df = df.iloc[:,-1]

        return [Balance(
            account_number=account_number,
            deposit_type=str_to_deposit_type(df[1]),
            branch_name=df[0],
            value = float(df[3].replace(",", "").replace("円", ""))
        )]


    def get_transaction_history(
        self,
        account_number: str,
        start: date = None,
        end: date = None,
        currency: CurrencyType = None,
    ) -> list[Transaction]:
        """Gets the transaction history. If start or end parameter is empty, return the history of current month.

        :param account_number: specify an account number.
        :param start: start date of transaction history. After the 1st of the month before the previous month.
        :param end: end date of transaction history. Until today.
        :param currency: currency of transaction history. But this parameter currently doesn't affect.
        """
        transaction = 'MB_R011N040'
        elem = self.find_element_to_be_clickable(By.ID, transaction)
        elem.click()
        # When there is the account select box
        try:
            select_account = 'lstAccSel'
            elem = self.find_element(By.NAME, select_account)
            select = Select(elem)
            for o in select.options:
                if o.text.endswith(account_number):
                    select.select_by_value(o.get_attribute("value"))
                    break
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

        if start is not None or end is not None:
            max_date = date.today()
            min_date = date(max_date.year, max_date.month, 1) + relativedelta(months=-2)
            if min_date <= start < end <= max_date:
                period = 'rdoInqMtdSpec'
                elem = self.find_elements(By.NAME, period)
                elem[1].click()
                Select(self.driver.find_element(By.NAME, 'lstDateFrmYear')).select_by_value(str(start.year))
                Select(self.driver.find_element(By.NAME, 'lstDateFrmMnth')).select_by_value(str(start.month))
                Select(self.driver.find_element(By.NAME, 'lstDateFrmDay')).select_by_value(str(start.day))

                Select(self.driver.find_element(By.NAME, 'lstDateToYear')).select_by_value(str(end.year))
                Select(self.driver.find_element(By.NAME, 'lstDateToMnth')).select_by_value(str(end.month))
                Select(self.driver.find_element(By.NAME, 'lstDateToDay')).select_by_value(str(end.day))
            else:
                raise AttributeError(f"date can be set between {min_date} and {max_date}")
        inquiry_transaction = '//*[@id="main"]/section[1]/input'
        elem = self.find_element(By.XPATH, inquiry_transaction)
        elem.click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", class_="n04110-t2")
        if table is None:
            return []

        df = pd.read_html(StringIO(str(table)))[0]
        if df is None:
            return []
        ret: list[Transaction] = []
        for d in df.iterrows():
            v: str = d[1].iloc[2].replace(",", "").replace("円", "")
            if v == "-":
                v: str = "-" + d[1].iloc[1].replace(",", "").replace("円", "")
            try:
                ret.append(Transaction(
                    dt=datetime.strptime(d[1].iloc[0], "%Y.%m.%d").date(),
                    content=d[1].iloc[3],
                    value=float(v),
                ))
            except ValueError:
                return ret

        return ret
