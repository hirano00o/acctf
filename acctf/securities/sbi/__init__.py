from abc import ABC
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from acctf.securities import Securities
from acctf.securities.model import Value
from acctf.securities.sbi.utils import get_formatted, AccountType, get_formatted_for_ul_tables


class SBI(Securities, ABC):
    _df_fund_specific: pd.DataFrame = None
    _df_fund_nisa_accum: pd.DataFrame = None
    _df_fund_old_nisa_accum: pd.DataFrame = None

    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)
        self.page.goto('https://www.sbisec.co.jp/ETGate')


    def login(self, user_id: str, password: str, totp: str | None = None):
        self.find_element('[name="user_id"]').fill(user_id)
        self.page.locator('[name="user_password"]').fill(password)

        self.page.locator('[name="ACT_login"]').click()
        return self

    def logout(self):
        try:
            self.page.locator('//*[@id="logoutM"]/a/img').click(timeout=self.timeout)
        except PlaywrightTimeoutError:
            self.page.locator('//*[@id="logout-button"]').click()

    def get_stock_specific(self) -> list[Value]:
        # 口座管理ページ
        self.find_element('//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 株式(現物)タブ
        self.page.get_by_role("link", name="株式(現物)").click()

        html = self.page.content().encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")
        if table is None or len(table) == 0:
            return []

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        return get_formatted(df, AccountType.jp)


    def get_stock_specific_us(self) -> list[Value]:
        # 口座管理ページ
        self.find_element('//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 口座(外貨建)ページ
        self.page.get_by_role("link", name="口座(外貨建)").click()
        # 株式（現物）タブ
        self.find_element('//*[@id="account-tab-layout"]/div/div[2]/div[2]/ul[1]/button[2]').click()
        html = self.page.content().encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("ul", class_="table-content table-primary-content")
        if table is None or len(table) < 2:
            return []

        return get_formatted_for_ul_tables(table[1])


    def get_fund_specific(self) -> list[Value]:
        if self._df_fund_specific is None:
            self._get_fund_all()
        return get_formatted(self._df_fund_specific, AccountType.jp)


    def get_fund_nisa_accum(self) -> list[Value]:
        if self._df_fund_nisa_accum is None:
            self._get_fund_all()
        return get_formatted(self._df_fund_nisa_accum, AccountType.jp)


    def get_fund_old_nisa_accum(self) -> list[Value]:
        if self._df_fund_old_nisa_accum is None:
            self._get_fund_all()
        return get_formatted(self._df_fund_old_nisa_accum, AccountType.jp)


    def _get_fund_all(self):
        # 口座管理ページ
        self.find_element('//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 投信タブ
        self.page.get_by_role("link", name="投信").click()

        html = self.page.content().encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")
        if table is None or len(table) == 0:
            return

        df = pd.read_html(StringIO(str(table)), header=0)
        for d in df:
            if d.columns[0] == '投資信託（金額/特定預り）':
                self._df_fund_specific = d
            elif d.columns[0] == '投資信託（金額/NISA預り（つみたて投資枠））':
                self._df_fund_nisa_accum = d
            elif d.columns[0] == '投資信託（金額/旧つみたてNISA預り）':
                self._df_fund_old_nisa_accum = d
