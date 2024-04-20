from abc import ABC
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from acctf.securities import Securities
from acctf.securities.model import Value
from acctf.securities.sbi.utils import get_formatted, AccountType


class SBI(Securities, ABC):
    _df_fund_specific: pd.DataFrame = None
    _df_fund_nisa_accum: pd.DataFrame = None
    _df_fund_old_nisa_accum: pd.DataFrame = None

    def __init__(self, driver: webdriver = None, timeout: float = 30):
        super().__init__(driver=driver, timeout=timeout)
        self.driver.get('https://www.sbisec.co.jp/ETGate')


    def login(self, user_id: str, password: str, totp: str | None = None):
        user_id_elem = self.find_element(By.NAME, 'user_id')
        user_id_elem.send_keys(user_id)
        user_pw_elem = self.driver.find_element(By.NAME, 'user_password')
        user_pw_elem.send_keys(password)

        self.driver.find_element(By.NAME, 'ACT_login').click()
        return self

    def logout(self):
        self.driver.find_element(By.XPATH, '//*[@id="logoutM"]/a/img').click()

    def get_stock_specific(self) -> list[Value]:
        # 口座管理ページ
        self.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 株式(現物)タブ
        self.find_element(By.LINK_TEXT, '株式(現物)').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")
        if table is None or len(table) == 0:
            return []

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        return get_formatted(df, AccountType.jp)


    def get_stock_specific_us(self) -> list[Value]:
        # 口座管理ページ
        self.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 口座(外貨建)ページ
        self.find_element(By.LINK_TEXT, '口座(外貨建)').click()
        # 株式（現物）タブ
        self.find_element(By.LINK_TEXT, '株式（現物）').click()
        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="100%")
        if table is None or len(table) == 0:
            return []

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        return get_formatted(df, AccountType.us)


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
        self.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 投信タブ
        self.find_element(By.LINK_TEXT, '投信').click()

        html = self.driver.page_source.encode('utf-8')
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
