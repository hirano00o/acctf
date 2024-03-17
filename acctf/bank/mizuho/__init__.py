from abc import ABC
from datetime import date, datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from acctf.bank import Bank, Balance, Transaction
from acctf.bank.model import str_to_deposit_type, CurrencyType


class Mizuho(Bank, ABC):
    def __init__(self):
        super().__init__()
        self.driver.get('https://web.ib.mizuhobank.co.jp/servlet/LOGBNK0000000B.do')


    def login(self, user_id: str, password: str, otp: str | None = None):
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


    def get_balance(self, account_number: str) -> list[Balance]:
        self.driver.find_element(By.ID, 'MB_R011N030').click()
        # When there is the account select box
        try:
            elem = self.driver.find_element(By.CLASS_NAME, 'n03000-t1')
            tr = iter(elem.find_elements(By.TAG_NAME, "tr"))
            # skip header
            next(tr)
            for num, t in enumerate(tr):
                if t.find_elements(By.TAG_NAME, "span")[2].text == account_number:
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
        self.driver.find_element(By.ID, 'MB_R011N040').click()
        # When there is the account select box
        try:
            elem = self.driver.find_element(By.NAME, 'lstAccSel')
            select = Select(elem)
            for o in select.options:
                if o.text.endswith(account_number):
                    select.select_by_value(o.get_attribute("value"))
                    break
        except NoSuchElementException as e:
            pass

        if start is not None or end is not None:
            max_date = date.today()
            min_date = date(max_date.year, max_date.month, 1) + relativedelta(months=-2)
            if min_date <= start < end <= max_date:
                self.driver.find_elements(By.NAME, 'rdoInqMtdSpec')[1].click()
                Select(self.driver.find_element(By.NAME, 'lstDateFrmYear')).select_by_value(str(start.year))
                Select(self.driver.find_element(By.NAME, 'lstDateFrmMnth')).select_by_value(str(start.month))
                Select(self.driver.find_element(By.NAME, 'lstDateFrmDay')).select_by_value(str(start.day))

                Select(self.driver.find_element(By.NAME, 'lstDateToYear')).select_by_value(str(end.year))
                Select(self.driver.find_element(By.NAME, 'lstDateToMnth')).select_by_value(str(end.month))
                Select(self.driver.find_element(By.NAME, 'lstDateToDay')).select_by_value(str(end.day))
        self.driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/input').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", class_="n04110-t2")

        df = pd.read_html(StringIO(str(table)))[0]
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
