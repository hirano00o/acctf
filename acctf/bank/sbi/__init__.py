import glob
import os
from pathlib import Path
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
from acctf.bank.sbi.model import AccountName


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
        self.driver.find_element(By.XPATH, '//nb-button-login/button').click()
        self.driver.set_window_size(1024, 3480)
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
                        value=float(d["残高"][0].replace(",", "").replace("円", ""))
                    )
                )

        return ret

    def get_transaction_history(
        self,
        account_number: str,
        start: date = None,
        end: date = None,
        currency: CurrencyType = CurrencyType.jpy,
        download_directory: Path = Path.cwd(),
        account_name: AccountName | str = AccountName.Representative,
    ) -> list[Transaction]:
        """Gets the transaction history. If start or end parameter is empty, return the history of current month.

        :param account_number: specify an account number.
        :param start: start date of transaction history. After the 1st of the month before the previous month.
        :param end: end date of transaction history. Until today.
        :param currency: currency of transaction history.
        :param download_directory: temporarily download directory. Specify the directory that it sets to the driver.
        :param account_name: account name. When you get the purpose account's transaction history, specify the account
        name with string.
        """
        if account_number != "" and account_number is not None:
            self.account_number = account_number
        if account_name != AccountName.Representative and currency != CurrencyType.jpy:
            raise AttributeError("currencies other than JPY can only be combined with the AccountName.Representative")

        exist_directory = False
        try:
            os.makedirs(download_directory)
        except FileExistsError:
            exist_directory = True

        download_path = f"{str(Path(download_directory))}/nyushukinmeisai_*.csv"

        self.wait_loading(By.CLASS_NAME, "loading-Server")

        details = 'm-icon-ps_details'
        elem = self.find_element_to_be_clickable(By.CLASS_NAME, details)
        elem.click()

        self.wait_loading(By.CLASS_NAME, "loadingServer")

        # 口座変更
        self._change_account(account_name=account_name)

        # 通貨変更
        self._change_currency(currency=currency, account_name=account_name)

        # 明細の表示
        self._get_transaction(start, end)

        try:
            # 明細のダウンロード
            file = self._download_transaction(download_full_path=download_path)
        except Exception as e:
            self._remove_download(download_directory=download_directory, file_path=file,
                                  exist_directory=exist_directory)
            raise e

        if file == "" or file is None:
            return []

        header = ["日付", "内容", "出金金額(円)", "入金金額(円)", "残高(円)", "メモ"]
        try:
            df = pd.read_csv(file, names=header, header=0, usecols=[0, 1, 2, 3], encoding="sjis")
        except Exception as e:
            self._remove_download(download_directory=download_directory, file_path=file,
                                  exist_directory=exist_directory)
            raise e

        if df is None:
            return []
        ret: list[Transaction] = []
        for d in df.iterrows():
            v: str = f"-{d[1].iloc[3]}" if pd.isnull(d[1].iloc[2]) else str(d[1].iloc[2])
            try:
                ret.append(Transaction(
                    dt=datetime.strptime(d[1].iloc[0], "%Y/%m/%d").date(),
                    content=d[1].iloc[1],
                    value=float(v.replace(",", "")),
                ))
            except ValueError:
                self._remove_download(download_directory=download_directory, file_path=file,
                                      exist_directory=exist_directory)
                return ret

        self._remove_download(download_directory=download_directory, file_path=file,
                              exist_directory=exist_directory)
        return ret

    def _change_account(self, account_name: AccountName | str):
        if account_name == AccountName.Representative:
            return

        self.find_element(By.XPATH, '//*[@id="acctBusPdCodeInput"]').click()
        time.sleep(1)

        if account_name == AccountName.Hybrid:
            self.find_element(By.XPATH, '//*[@id="acctBusPdCodeInput_item_1"]').click()
            return

        # 目的別口座
        self.find_element(By.XPATH, f'//li[contains(text(), "{account_name}")]').click()

    def _change_currency(self, currency: CurrencyType, account_name: AccountName | str):
        if account_name != AccountName.Representative:
            return

        currency_map: dict = {
            CurrencyType.jpy: '//*[@id="crncyCode_item_0"]',
            CurrencyType.usd: '//*[@id="crncyCode_item_1"]',
        }
        select_currency = '//*[@id="crncyCode"]/span[2]'
        self.find_element(By.XPATH, select_currency).click()
        time.sleep(1)
        e = self.find_element(By.XPATH, currency_map[currency])
        ActionChains(self.driver).move_to_element(e).perform()
        e.click()
        time.sleep(1)

    def _download_transaction(self, download_full_path: str) -> str:
        e = self.find_element(By.CSS_SELECTOR, '.m-boxError.ng-star-inserted', False)
        if e is not None:
            return ""

        # ダウンロード
        self.find_element(By.XPATH, '//section/div/div[1]/nav/ul/li[2]/ul/li[2]').click()
        # CSV
        self.find_element(By.XPATH, '//span[contains(text(), "CSV")]').click()

        timeout_sec = 3
        while not glob.glob(download_full_path):
            time.sleep(1)
            timeout_sec -= 1
            if timeout_sec < 0:
                raise Exception("downloads are taking too long")

        return glob.glob(download_full_path)[0]

    def _remove_download(self, download_directory: Path, file_path: str, exist_directory: bool):
        if os.path.isfile(file_path):
            os.remove(file_path)
        if not exist_directory:
            os.removedirs(download_directory)

    def _get_transaction(
        self,
        start: date = None,
        end: date = None,
    ) -> pd.DataFrame | None:
        default_period_text = "最新100明細"
        period_text = "期間指定"
        # 絞り込み
        elem = self.find_element(By.XPATH, "//section/div/div[2]/div[1]/nav/ul/li[1]")
        elem.click()
        time.sleep(1)

        if start is not None:
            max_date = date.today()
            min_date = date(max_date.year - 7, 1, 1)
            if end is None:
                end = max_date
            if not min_date <= start < end <= max_date:
                raise AttributeError(f"date can be set between {min_date} and {max_date}")

            period_value = self.find_element(By.XPATH, '//*[@id="filterTerm"]/span[2]').text
            if period_value == default_period_text:
                # 期間指定
                self.find_element(By.XPATH, '//*[@id="filterTerm"]').click()
                time.sleep(1)
                self.find_element(By.XPATH, '//*[@id="filterTerm_item_5"]').click()
                time.sleep(1)

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
            e = self.find_elements(By.XPATH, f'//li[contains(text(), "{end.year}年")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()
            self.find_elements(By.XPATH, '//p[2]/nb-simple-select/span/span[2]')[1].click()
            time.sleep(1)
            e = self.find_elements(By.XPATH, f'//li[contains(text(), "{end.month}月")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()
            self.find_elements(By.XPATH, '//p[3]/nb-simple-select/span/span[2]')[1].click()
            time.sleep(1)
            e = self.find_elements(By.XPATH, f'//li[contains(text(), "{end.day}日")]')[1]
            ActionChains(self.driver).move_to_element(e).perform()
            e.click()
        else:
            period_value = self.find_element(By.XPATH, '//*[@id="filterTerm"]/span[2]').text
            if period_value == period_text:
                # Change to 最新100明細
                self.find_element(By.XPATH, '//*[@id="filterTerm"]').click()
                time.sleep(1)
                self.find_element(By.XPATH, '//*[@id="filterTerm_item_0"]').click()
                time.sleep(1)

        # 適用
        display = '.m-btnEm-m.m-btnEffectAnc'
        self.find_element(By.CSS_SELECTOR, display).click()

        self.wait_loading(By.CLASS_NAME, "loadingServer")

    def _get_account_info(self):
        branch_name = '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[1]'
        elem = self.find_element(By.XPATH, branch_name)
        self.branch_name = elem.text

        self.account_number = self.driver.find_element(
            By.XPATH,
            '/html/body/app/div[1]/ng-component/div/main/ng-component/div[1]/div/div/div/div/div/span/span[3]').text
