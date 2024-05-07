import time
from abc import ABC
from datetime import date, datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from acctf.bank import Bank, Balance, Transaction
from acctf.bank.model import str_to_deposit_type, CurrencyType
from acctf.utils.format import format_displayed_money


class SBI(Bank, ABC):
    account_number = ""
    branch_name = ""

    def __init__(self, driver: webdriver = None, timeout: float = 30):
        super().__init__(driver=driver, timeout=timeout)
        self.driver.get('https://www.netbk.co.jp/contents/pages/wpl010101/i010101CT/DI01010210')


    def login(self, user_id: str, password: str, totp: str | None = None):
        user_id_elem = self.find_element(By.ID, 'userNameNewLogin')
        user_id_elem.send_keys(user_id)

        user_pw_elem = self.find_element(By.ID, 'loginPwdSet')
        user_pw_elem.send_keys(password)
        self.driver.find_element(By.TAG_NAME, 'button').click()
        self.driver.set_window_size(1024, 1000)
        self._get_account_info()

        return self


    def logout(self):
        self.driver.find_element(By.CSS_SELECTOR, '.header_logout.ng-star-inserted').click()


    def get_balance(self, account_number: str) -> list[Balance]:
        if account_number != "" and account_number is not None:
            self.account_number = account_number

        balance = 'm-icon-ps_balance'
        elem = self.find_element_to_be_clickable(By.CLASS_NAME, balance)
        elem.click()

        self.wait_loading(By.CLASS_NAME, "loadingServer")

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("table")
        if table is None or len(table) == 0:
            return []

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
        :param currency: currency of transaction history.
        """
        if account_number != "" and account_number is not None:
            self.account_number = account_number

        self.wait_loading(By.CLASS_NAME, "loading-Server")

        details = 'm-icon-ps_details'
        elem = self.find_element_to_be_clickable(By.CLASS_NAME, details)
        elem.click()

        self.wait_loading(By.CLASS_NAME, "loadingServer")

        # 代表口座
        if currency is None:
            currency = CurrencyType.jpy

        df = self._get_transaction(start, end, currency)
        if currency == CurrencyType.jpy:
            # ハイブリッド預金(Only Yen)
            hybrid = '//ng-component/section/div/div[3]/div[1]/div[1]/div[2]/nb-select/div/div[1]'
            e = self.find_elements(By.XPATH, hybrid)
            if len(e) > 0:
                e[0].click()
                time.sleep(1)
                elem = self.find_element(By.XPATH, '//*[@id="form3-menu"]/li[2]')
                elem.click()
                df_hybrid = self._get_transaction(start, end)
                if df is None and df_hybrid is None:
                    return []
                df = pd.concat([df, df_hybrid]).sort_values("日付")

        if df is None:
            return []
        ret: list[Transaction] = []
        for d in df.iterrows():
            v: str = ""
            if pd.isnull(d[1].iloc[2]):
                v = format_displayed_money(d[1].iloc[3])
            else:
                v = "-" + format_displayed_money(d[1].iloc[2])
            try:
                ret.append(Transaction(
                    dt=datetime.strptime(d[1].iloc[0], "%Y年%m月%d日").date(),
                    content=d[1].iloc[1],
                    value=float(v),
                ))
            except ValueError:
                return ret

        return ret

    def _get_transaction(
        self,
        start: date = None,
        end: date = None,
        currency: CurrencyType = CurrencyType.jpy,
    ) -> pd.DataFrame | None:
        currency_map: dict = {
            CurrencyType.jpy: '//nb-select/div/div[2]/ul/li[1]',
            CurrencyType.usd: '//nb-select/div/div[2]/ul/li[2]',
        }
        if start is not None:
            max_date = date.today()
            min_date = date(max_date.year-7, 1, 1)
            if end == None:
                end = max_date
            if min_date <= start < end <= max_date:
                # 期間指定選択
                period = '//li[5]/label'
                elem = self.find_element(By.XPATH, period)
                elem.click()
            else:
                raise AttributeError(f"date can be set between {min_date} and {max_date}")

            # 開始日
            # Sleep until an animation ended
            self.find_element(By.XPATH, '//p[1]/nb-simple-select/span/span[2]').click()
            time.sleep(1)
            self.find_element(By.XPATH, f'//li[contains(text(), "{start.year}年")]').click()
            self.find_element(By.XPATH, '//p[2]/nb-simple-select/span/span[2]').click()
            time.sleep(1)
            self.find_element(By.XPATH, f'//li[contains(text(), "{start.month}月")]').click()
            self.find_element(By.XPATH, '//p[3]/nb-simple-select/span/span[2]').click()
            time.sleep(1)
            self.find_element(By.XPATH, f'//li[contains(text(), "{start.day}日")]').click()

            # 終了日
            self.find_elements(By.XPATH, '//p[1]/nb-simple-select/span/span[2]')[1].click()
            time.sleep(1)
            e = self.find_elements(By.XPATH, f'//li[contains(text(), " {end.year}年 ")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()
            self.find_elements(By.XPATH, '//p[2]/nb-simple-select/span/span[2]')[1].click()
            time.sleep(1)
            e = self.find_elements(By.XPATH, f'//li[contains(text(), " {end.month}月 ")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()
            self.find_elements(By.XPATH, '//p[3]/nb-simple-select/span/span[2]')[1].click()
            time.sleep(1)
            e = self.find_elements(By.XPATH, f'//li[contains(text(), " {end.day}日 ")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()

        # 通貨選択(代表口座のみ)
        select_currency = '//nb-select/div/div[1]/span[2]'
        elem = self.find_elements(By.XPATH, select_currency)
        elem[1].click()
        e = self.find_elements(By.XPATH, currency_map[currency])[1]
        ActionChains(self.driver).move_to_element(e).perform()
        e.click()

        # 表示選択
        display = '.m-btnEm-m.m-btnEffectAnc'
        self.find_element(By.CSS_SELECTOR, display).click()

        self.wait_loading(By.ID, "loadWrap")

        _continue = '.m-btn_icon_txt.ng-tns-c3-3.ng-star-inserted'
        continue_button = self.find_elements(By.CSS_SELECTOR, _continue, False)
        while continue_button is not None:
            continue_button[0].click()
            continue_button = self.find_elements(By.CSS_SELECTOR, _continue, False)
            self.wait_loading(By.CSS_SELECTOR, '.show-loading.ng-tns-c3-3.ng-star-inserted')

        html = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table")
        return None if table is None else pd.read_html(StringIO(str(table)))[0]

    def _get_account_info(self):
        branch_name = '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[1]'
        elem = self.find_element(By.XPATH, branch_name)
        self.branch_name = elem.text

        self.account_number= self.driver.find_element(
            By.XPATH,
            '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[3]').text
