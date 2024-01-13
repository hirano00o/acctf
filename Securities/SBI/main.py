from io import StringIO
from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from Securities.Base.main import BaseSecurities, Value
import pandas as pd


def _get_formatted(df: pd.DataFrame) -> List[Value]:
    df = df.drop(df.index[0]).iloc[:,0:3]
    code_df = df[::2].iloc[:,[1]].reset_index(drop=True).set_axis(['name'], axis=1)
    val_df = df[1::2].reset_index(drop=True).set_axis(['amount', 'acquisition_val', 'current_val'], axis=1)
    ret: List[Value] = []
    for _, row in pd.concat([code_df, val_df], axis=1).iterrows():
        ret.append(Value(row['name'], row['amount'], row['acquisition_val'], row['current_val']))

    return ret


class SBI(BaseSecurities):
    _df_fund_specific: pd.DataFrame
    _df_fund_nisa_accum: pd.DataFrame
    _df_fund_old_nisa_accum: pd.DataFrame

    def __init__(self):
        super().__init__()
        self.driver.get('https://www.sbisec.co.jp/ETGate')


    def login(self, user_id: str, password: str):
        user_id_elem = self.driver.find_element(By.NAME, 'user_id')
        user_id_elem.send_keys(user_id)
        user_pw_elem = self.driver.find_element(By.NAME, 'user_password')
        user_pw_elem.send_keys(password)

        self.driver.find_element(By.NAME, 'ACT_login').click()
        return self


    def get_stock_specific(self) -> List[Value]:
        # 口座管理ページ
        self.driver.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 株式(現物)タブ
        self.driver.find_element(By.LINK_TEXT, '株式(現物)').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        return _get_formatted(df)


    def get_fund_specific(self) -> List[Value]:
        # 口座管理ページ
        self.driver.find_element(By.XPATH, '//*[@id="link02M"]/ul/li[3]/a/img').click()
        # 投信タブ
        self.driver.find_element(By.LINK_TEXT, '投信').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table", border="0", cellpadding="1", cellspacing="1", width="400")

        df = pd.read_html(StringIO(str(table)), header=0)
        for d in df:
            if d.columns[0] == '投資信託（金額/特定預り）':
                self._df_fund_specific = d
            elif d.columns[0] == '投資信託（金額/NISA預り（つみたて投資枠））':
                self._df_fund_nisa_accum = d
            elif d.columns[0] == '投資信託（金額/旧つみたてNISA預り）':
                self._df_fund_old_nisa_accum = d

        return _get_formatted(self._df_fund_specific)


    def get_fund_nisa_accum(self) -> List[Value]:
        raise NotImplementedError()


    def get_fund_old_nisa_accum(self) -> List[Value]:
        raise NotImplementedError()


    def concat(self):
        raise NotImplementedError()
