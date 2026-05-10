from abc import ABC
from datetime import date, datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from acctf.bank import Bank, Balance, Transaction
from acctf.bank.model import str_to_deposit_type, CurrencyType


class Mizuho(Bank, ABC):
    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)
        self.page.goto('https://web.ib.mizuhobank.co.jp/servlet/LOGBNK0000000B.do')


    def login(self, user_id: str, password: str, totp: str | None = None):
        self.find_element('[name="txbCustNo"]').fill(user_id)
        self.page.locator('[name="N00000-next"]').click()

        self.find_element('[name="PASSWD_LoginPwdInput"]').fill(password)
        self.page.locator('#btn_login').click()

        try:
            elem = self.find_element('//*[@id="button-section"]/a/img')
        except PlaywrightTimeoutError:
            pass
        else:
            elem.click()

        return self


    def logout(self):
        self.page.locator('//*[@id="side-menu"]/div[1]/a/img').click()


    def get_balance(self, account_number: str) -> list[Balance]:
        balance = 'MB_R011N030'
        self.find_element_to_be_clickable(f'#{balance}').click()
        # When there is the account select box
        try:
            table_loc = self.find_element('.n03000-t1')
            rows = table_loc.locator('tr').all()
            # skip header (rows[0]) and iterate the rest
            for num, t in enumerate(rows[1:]):
                spans = t.locator('span').all()
                if len(spans) > 2 and spans[2].inner_text() == account_number:
                    t.locator(f'[name="chkAccChkBx_{str(num).zfill(3)}"]').click()
                    break
            self.page.locator('//*[@id="main"]/section/input').click()
        except PlaywrightTimeoutError:
            pass

        html = self.page.content().encode('utf-8')
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
        self.find_element_to_be_clickable(f'#{transaction}').click()
        # When there is the account select box
        try:
            select_loc = self.find_element('[name="lstAccSel"]')
            for o in select_loc.locator('option').all():
                if o.inner_text().endswith(account_number):
                    value = o.get_attribute("value")
                    select_loc.select_option(value=value)
                    break
        except PlaywrightTimeoutError:
            pass

        if start is not None or end is not None:
            max_date = date.today()
            min_date = date(max_date.year, max_date.month, 1) + relativedelta(months=-2)
            if min_date <= start < end <= max_date:
                self.find_elements('[name="rdoInqMtdSpec"]').nth(1).click()
                self.page.locator('[name="lstDateFrmYear"]').select_option(value=str(start.year))
                self.page.locator('[name="lstDateFrmMnth"]').select_option(value=str(start.month))
                self.page.locator('[name="lstDateFrmDay"]').select_option(value=str(start.day))

                self.page.locator('[name="lstDateToYear"]').select_option(value=str(end.year))
                self.page.locator('[name="lstDateToMnth"]').select_option(value=str(end.month))
                self.page.locator('[name="lstDateToDay"]').select_option(value=str(end.day))
            else:
                raise AttributeError(f"date can be set between {min_date} and {max_date}")
        self.find_element('//*[@id="main"]/section[1]/input').click()

        html = self.page.content().encode('utf-8')
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
