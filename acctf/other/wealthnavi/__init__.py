from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from acctf import Base
from acctf.other.wealthnavi.model import Asset
from acctf.utils.format import format_displayed_money


class WealthNavi(Base):
    def __init__(self):
        super().__init__()
        self.driver.get('https://invest.wealthnavi.com/login')

    def login(self, user_id: str, password: str, otp: str | None = None):
        user_id_elem = self.driver.find_element(By.ID, 'username')
        user_id_elem.send_keys(user_id)

        user_pw_elem = self.driver.find_element(By.ID, 'password')
        user_pw_elem.send_keys(password)

        self.driver.find_element(By.ID, 'login').click()

        if otp is not None:
            otp_elem = self.driver.find_element(By.ID, 'code')
            otp_elem.send_keys(int(otp))

            self.driver.find_element(By.ID, 'authentication-code-login').click()

        return self

    def get_valuation(self) -> list[Asset]:
        self.driver.set_window_size(1024, 600)
        self.driver.find_element(By.PARTIAL_LINK_TEXT, 'ポートフォリオ').click()

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", id="assets-class-data")

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        df = df.iloc[:,0:3]
        ret: list[Asset] = []
        for d in df.iterrows():
            v, plv = format_displayed_money(d[1].iloc[1]), format_displayed_money(d[1].iloc[2])
            if v == "-":
                v = 0
            if plv == "-":
                plv = 0
            try:
                ret.append(Asset(
                    name=d[1].iloc[0],
                    value=float(v),
                    pl_value=float(plv),
                ))
            except ValueError:
                return ret

        return ret
