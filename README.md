# acctf

acctfは、銀行や証券会社をスクレイピングして入出金履歴、株や投信の保有数や取得価額、現在価格を取得するライブラリです。

下記の銀行や証券会社等に対応しています。
### 証券会社
* SBI証券
  * 円建て
    * 株式
      * 株式(現物)
    * 投信
      * 投資信託（金額/特定預り）
      * 投資信託（金額/NISA預り（つみたて投資枠））
      * 投資信託（金額/旧つみたてNISA預り）
  * 外貨建て(USのみ)
    * 株式
      * 株式(現物)

### 銀行
* 住信SBIネット銀行
  * 預金(ハイブリッド含む)(円のみ)
  * 入出金履歴
    * 代表口座
    * ハイブリッド預金口座
    * 目的別口座

### その他
* WealthNavi(円表示のみ)
  * 各資産クラス

# 利用方法

## インストール

```console
pip install acctf
playwright install chromium
```

uvを利用する場合:

```console
uv add acctf
uv run playwright install chromium
```

> **注**: v0.6.0 以降、ブラウザ自動化に [Playwright](https://playwright.dev/python/) を採用しています。
> arm64 Linux (Raspberry Pi 5 など) では Chromium のみサポートされ、Firefox は動作しません。

## サンプル

### 証券会社

```python
from acctf.securities.sbi import SBI
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    sbi = SBI(page=page).login("<ユーザID>", "<パスワード>")
    stocks = sbi.get_stock_specific()
    print("銘柄, 数量, 取得単価, 現在値")
    for s in stocks:
        print(f"{s.name}, {s.amount}, {s.acquisition_value}, {s.current_value}")

    sbi.logout()
    browser.close()
```

```console
銘柄, 数量, 取得単価, 現在値
0000 銘柄1, 1000, 1234, 2345
1111 銘柄2, 1500, 789, 987
2222 銘柄3, 2000, 3450, 3456
```

### 銀行

#### 預金

```python
from acctf.bank.sbi import SBI
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    sbi = SBI(page=page).login("<ユーザID>", "<パスワード>")
    b = sbi.get_balance("7654321")
    print(f"口座番号, 店舗, 残高, 口座タイプ")
    print(f"{b[0].account_number}, {b[0].branch_name}, {b[0].value}, {b[0].deposit_type}")

    sbi.logout()
    browser.close()
```

```console
口座番号, 店舗, 残高, 口座タイプ
7654321, 本店, 1234567.0, DepositType.ordinary
```

#### 入出金履歴

住信SBIネット銀行はUIの変更に伴い、履歴のCSVをダウンロードしてデータを取得する方式です。
ブラウザコンテキストを `accept_downloads=True` で生成する必要があります。
また、ダウンロードしたCSVファイルはデータ取得後に削除されます。

```python
from pathlib import Path

from acctf.bank.sbi import SBI, AccountName
from acctf.bank import CurrencyType
from playwright.sync_api import sync_playwright
from datetime import date

download_directory = str(Path.cwd()) + "/tmp"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # CSVダウンロードのため accept_downloads=True が必須
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    sbi = SBI(page=page).login("<ユーザID>", "<パスワード>")
    hist = sbi.get_transaction_history(
        "7654321",
        date(2023, 12, 1),
        date(2023, 12, 31),
        download_directory=download_directory,
        currency=CurrencyType.jpy,
        account_name=AccountName.Representative,  # 代表口座
    )
    hist += sbi.get_transaction_history(
        "7654321",
        date(2023, 12, 1),
        date(2023, 12, 31),
        download_directory=download_directory,
        currency=CurrencyType.jpy,
        account_name=AccountName.Hybrid,  # ハイブリッド預金口座
    )

    print(f"日付, 取引内容, 金額")
    for h in hist:
        print(f"{h.date}, {h.content}, {h.value}")

    sbi.logout()
    browser.close()
```

### その他

#### WealthNavi

```python
from acctf.other.wealthnavi import WealthNavi
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    w = WealthNavi(page=page).login("<ユーザID>", "<パスワード>", "<TOTP>")
    # Time-based One Time Passwordを設定していない場合
    # w = WealthNavi(page=page).login("<ユーザID>", "<パスワード>")
    print("資産クラス, 現在価格, 損益")
    for h in w.get_valuation():
        print(f"{h.name}, {h.value}, {h.pl_value}")

    w.logout()
    browser.close()
```

```console
資産クラス, 現在価格, 損益
米国株(VTI), 123456.0, 12345.0
日欧株(VEA), 123456.0, 12345.0
新興国株(VWO), 123456.0, 12345.0
債券(AGG), 123456.0, 12345.0
金(GLD), 123456.0, 12345.0
金(IAU), 123456.0, 12345.0
不動産(IYR), 123456.0, 12345.0
現金, 123456.0, 0.0
```

# arm64 環境について

Raspberry Pi 5 などの arm64 Linux 環境では、Playwright が公式に提供しているブラウザバイナリは **Chromium のみ** です。Firefox および branded Chrome は arm64 Linux では動作しません。

公式 Docker イメージ `mcr.microsoft.com/playwright/python` は linux/amd64 / linux/arm64 の multi-arch ビルドが提供されているため、Kubernetes クラスタ (arm64) 上でも追加設定なしに利用できます。Docker での実行サンプルは [`examples/`](examples/) を参照してください。

# v0.5.x からの移行

v0.6.0 で Selenium から Playwright へ移行しました。コンストラクタが `driver=` (Selenium WebDriver) から `page=` (Playwright Page) に変わります。

```python
# v0.5.x (Selenium)
from selenium import webdriver
driver = webdriver.Chrome()
sbi = SBI(driver=driver).login(...)

# v0.6.0 (Playwright)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    sbi = SBI(page=page).login(...)
```

`timeout` の単位が秒 (`30`) からミリ秒 (`30000`) に変わっています。

# 開発

このリポジトリは [uv](https://docs.astral.sh/uv/) で依存関係を管理しています。

## セットアップ

```console
uv sync
uv run playwright install chromium
```

## ビルド

```console
uv build
```

`dist/` 配下にホイール (`.whl`) と sdist (`.tar.gz`) が生成されます。

## PyPIへの公開

```console
uv publish
```
