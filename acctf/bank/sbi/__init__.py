import os
from pathlib import Path
import time
from abc import ABC
from datetime import date, datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Page

from acctf.bank import Bank, Balance, Transaction
from acctf.bank.model import str_to_deposit_type, CurrencyType
from acctf.bank.sbi.model import AccountName


class SBI(Bank, ABC):
    account_number = ""
    branch_name = ""

    def __init__(self, page: Page, timeout: int = 30000):
        super().__init__(page=page, timeout=timeout)
        self.page.goto('https://www.netbk.co.jp/contents/pages/wpl010101E/i010101CT/DI01010240')

    def login(self, user_id: str, password: str, totp: str | None = None):
        self.find_element('input[name="username"]').fill(user_id)
        self.find_element('ul.ren_btn._ren_main a._ren_fill_blue').click()
        self.find_element('input#loginPwd').fill(password)
        self.find_element('ul._login_spec button._ren_fill_blue').click()
        self.page.set_viewport_size({"width": 1024, "height": 3480})
        time.sleep(1)
        self._get_account_info()

        return self

    def logout(self):
        self.page.locator('.header_logout.ng-star-inserted').click()

    def get_balance(self, account_number: str) -> list[Balance]:
        if account_number != "" and account_number is not None:
            self.account_number = account_number

        self.page.goto('https://www.netbk.co.jp/contents/pages/wpl020101A/i020101CT/DI02010105')

        self.wait_loading('.loadingServer')

        html = self.page.content().encode('utf-8')
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
        :param download_directory: temporarily download directory. The browser context must be created with
            ``accept_downloads=True``.
        :param account_name: account name. When you get the purpose account's transaction history, specify the account
        name with string.
        """
        if account_number != "" and account_number is not None:
            self.account_number = account_number
        if account_name != AccountName.Representative and currency != CurrencyType.jpy:
            raise AttributeError("currencies other than JPY can only be combined with the AccountName.Representative")

        download_dir = Path(download_directory)
        exist_directory = False
        try:
            os.makedirs(download_dir)
        except FileExistsError:
            exist_directory = True

        self.wait_loading('.loading-Server')

        self.page.goto('https://www.netbk.co.jp/contents/pages/wpl020201/i020201CT/DI02020100')

        self.wait_loading('.loadingServer')

        # 口座変更
        self._change_account(account_name=account_name)

        # 通貨変更
        self._change_currency(currency=currency, account_name=account_name)

        # 明細の表示
        self._get_transaction(start, end)

        file = ""
        try:
            # 明細のダウンロード
            file = self._download_transaction(download_directory=download_dir)
        except Exception as e:
            self._remove_download(download_directory=download_dir, file_path=file,
                                  exist_directory=exist_directory)
            raise e

        if file == "" or file is None:
            return []

        header = ["日付", "内容", "出金金額(円)", "入金金額(円)", "残高(円)", "メモ"]
        try:
            # csv sample
            # "日付","内容","出金金額(円)","入金金額(円)","残高(円)","メモ"
            # "2025/01/01","利息",,"1","100,000","-"
            # "2025/01/01","国税","1",,"100,000","-"
            df = pd.read_csv(file, names=header, header=0, usecols=[0, 1, 2, 3], encoding="sjis")
        except Exception as e:
            self._remove_download(download_directory=download_dir, file_path=file,
                                  exist_directory=exist_directory)
            raise e

        if df is None:
            return []
        ret: list[Transaction] = []
        for d in df.iterrows():
            v: str = f"-{d[1].iloc[2]}" if pd.isnull(d[1].iloc[3]) else str(d[1].iloc[3])
            try:
                ret.append(Transaction(
                    dt=datetime.strptime(d[1].iloc[0], "%Y/%m/%d").date(),
                    content=d[1].iloc[1],
                    value=float(v.replace(",", "")),
                ))
            except ValueError:
                self._remove_download(download_directory=download_dir, file_path=file,
                                      exist_directory=exist_directory)
                return ret

        self._remove_download(download_directory=download_dir, file_path=file,
                              exist_directory=exist_directory)
        return ret

    def _change_account(self, account_name: AccountName | str):
        if account_name == AccountName.Representative:
            return

        self.find_element('//*[@id="acctBusPdCodeInput"]').click()
        time.sleep(1)

        if account_name == AccountName.Hybrid:
            self.find_element('//*[@id="acctBusPdCodeInput_item_1"]').click()
            return

        # 目的別口座
        self.find_element(f'//li[contains(text(), "{account_name}")]').click()

    def _change_currency(self, currency: CurrencyType, account_name: AccountName | str):
        if account_name != AccountName.Representative:
            return

        currency_map: dict = {
            CurrencyType.jpy: '//*[@id="crncyCode_item_0"]',
            CurrencyType.usd: '//*[@id="crncyCode_item_1"]',
        }
        select_currency = '//*[@id="crncyCode"]/span[2]'
        self.find_element(select_currency).click()
        time.sleep(1)
        e = self.find_element(currency_map[currency])
        e.hover()
        e.click()
        time.sleep(1)

    def _download_transaction(self, download_directory: Path) -> str:
        e = self.find_element('.m-boxError.ng-star-inserted', has_raised=False)
        if e is not None:
            return ""

        with self.page.expect_download(timeout=self.timeout) as dl_info:
            # ダウンロード
            self.find_element('//section/div/div[1]/nav/ul/li[2]/ul/li[2]').click()
            # CSV
            self.find_element('//span[contains(text(), "CSV")]').click()

        download = dl_info.value
        dest = str(Path(download_directory) / download.suggested_filename)
        download.save_as(dest)
        return dest

    def _remove_download(self, download_directory: Path, file_path: str, exist_directory: bool):
        if file_path and os.path.isfile(file_path):
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
        self.find_element("//section/div/div[2]/div[1]/nav/ul/li[1]").click()
        time.sleep(1)

        if start is not None:
            max_date = date.today()
            min_date = date(max_date.year - 7, 1, 1)
            if end is None:
                end = max_date
            if not min_date <= start < end <= max_date:
                raise AttributeError(f"date can be set between {min_date} and {max_date}")

            period_value = self.find_element('//*[@id="filterTerm"]/span[2]').inner_text()
            if period_value == default_period_text:
                # 期間指定
                self.find_element('//*[@id="filterTerm"]').click()
                self.find_element('.ui-menu-item.ng-tns-c4-4.ng-star-inserted')
                self.find_element('//*[@id="filterTerm_item_5"]').click()
                self.find_element('.term-date-slc.ng-tns-c3-3.ng-star-inserted')

            # 開始日
            self.find_element('//p[1]/nb-simple-select/span/span[2]').click()
            self.find_element('.ui-menu-item.ng-tns-c8-7.ng-star-inserted')
            self.find_element(f'//li[contains(text(), " {start.year}年")]').click()
            self.find_element('//p[2]/nb-simple-select/span/span[2]').click()
            self.find_element('.ui-menu-item.ng-tns-c8-8.ng-star-inserted')
            self.find_element(f'//li[contains(text(), " {start.month}月")]').click()
            self.find_element('//p[3]/nb-simple-select/span/span[2]').click()
            self.find_element('.ui-menu-item.ng-tns-c8-9.ng-star-inserted')
            self.find_element(f'//li[contains(text(), " {start.day}日")]').click()

            # 終了日
            self.find_elements('//p[1]/nb-simple-select/span/span[2]').nth(1).click()
            self.find_element('.ui-menu-item.ng-tns-c8-10.ng-star-inserted')
            e = self.find_elements(f'//li[contains(text(), " {end.year}年")]').nth(1)
            e.hover()
            e.click()
            self.find_elements('//p[2]/nb-simple-select/span/span[2]').nth(1).click()
            self.find_element('.ui-menu-item.ng-tns-c8-11.ng-star-inserted')
            e = self.find_elements(f'//li[contains(text(), " {end.month}月")]').nth(1)
            e.hover()
            e.click()
            self.find_elements('//p[3]/nb-simple-select/span/span[2]').nth(1).click()
            self.find_element('.ui-menu-item.ng-tns-c8-12.ng-star-inserted')
            e = self.find_elements(f'//li[contains(text(), " {end.day}日")]').nth(1)
            e.hover()
            e.click()
        else:
            period_value = self.find_element('//*[@id="filterTerm"]/span[2]').inner_text()
            if period_value == period_text:
                # Change to 最新100明細
                self.find_element('//*[@id="filterTerm"]').click()
                self.find_element('.ui-menu-item.ng-tns-c4-4.ng-star-inserted')
                self.find_element('//*[@id="filterTerm_item_0"]').click()

        # 適用
        self.find_element('.m-btnEm-m.m-btnEffectAnc').click()

        self.wait_loading('.loadingServer')

    def _get_account_info(self):
        branch_name = '//*[@id="after-loading-zandaka-area"]/div/div/div/div/div/span/span[1]'
        self.branch_name = self.find_element(branch_name).inner_text()

        self.account_number = self.page.locator(
            '//*[@id="after-loading-zandaka-area"]/div/div/div/div/div/span/span[3]'
        ).inner_text()
