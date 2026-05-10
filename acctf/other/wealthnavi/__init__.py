from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page

from acctf import Base
from acctf.other.wealthnavi.model import Asset
from acctf.utils.format import format_displayed_money
from acctf.utils.totp import get_code


class WealthNavi(Base):
    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)
        self.page.goto('https://invest.wealthnavi.com/login')

    def login(self, user_id: str, password: str, totp: str | None = None):
        self.find_element('#username').fill(user_id)
        self.page.locator('[name="action"]').click()
        self.page.locator('#password').fill(password)
        self.page.locator('[name="action"]').nth(1).click()

        if totp is not None:
            self.find_element('#code').fill(str(get_code(totp)))
            self.page.locator('[name="action"]').click()

        return self

    def logout(self):
        self.page.locator('.logout-submit').click()

    def get_valuation(self) -> list[Asset]:
        self.page.set_viewport_size({"width": 1024, "height": 600})
        self.find_element('a:has-text("ポートフォリオ")').click()

        html = self.page.content().encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", id="assets-class-data")
        if table is None:
            return []

        df = pd.read_html(StringIO(str(table)), header=0)[0]
        df = df.iloc[:,0:3]
        if df is None:
            return []
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
