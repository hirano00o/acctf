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
* みずほ銀行(円のみ)
  * 預金
  * 入出金履歴
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
```

## サンプル

### 証券会社

```python
from acctf.securities.sbi import SBI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

sbi = SBI(driver=driver).login("<ユーザID>", "<パスワード>")
stocks = sbi.get_stock_specific()
print("銘柄, 数量, 取得単価, 現在値")
for s in stocks:
  print(f"{s.name}, {s.amount}, {s.acquisition_value}, {s.current_value}")

sbi.logout()
sbi.close()
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
from acctf.bank.mizuho import Mizuho
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

mizuho = Mizuho(driver=driver).login("<ユーザID>", "<パスワード>")
b = mizuho.get_balance("7654321")
print(f"口座番号, 店舗, 残高, 口座タイプ")
print(f"{b[0].account_number}, {b[0].branch_name}, {b[0].value}, {b[0].deposit_type}")

mizuho.logout()
mizuho.close()
```

```console
口座番号, 店舗, 残高, 口座タイプ
7654321, 本店, 1234567.0, DepositType.ordinary
```

#### 入出金履歴

下記はみずほ銀行の例です。

```python
from acctf.bank.mizuho import Mizuho
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

mizuho = Mizuho(driver=driver).login("<ユーザID>", "<パスワード>")
hist = mizuho.get_transaction_history("7654321")
# You can also specify the start/end date.
# hist = mizuho.get_transaction_history("7654321", date(2023, 12, 1), date(2023, 12, 31))
print(f"日付, 取引内容, 金額")
for h in hist:
  print(f"{h.date}, {h.content}, {h.value}")

mizuho.logout()
mizuho.close()
```

```console
日付, 取引内容, 金額
2023-12-01, ＡＴＭ引き出し, -10000.0
2024-12-20, 給与, 200000.0
```

住信SBIネット銀行はUIの変更に伴い、履歴のCSVをダウンロードしてデータを取得する方式に変更しました。そのため、ドライバの設定時にダウンロードディレクトリを指定してください。
また、ダウンロードしたCSVファイルはデータ取得後に削除されます。

```python
from pathlib import Path

from acctf.bank.sbi import SBI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date

from acctf.bank.sbi import AccountName
from acctf.bank import CurrencyType

download_directory = str(Path.cwd()) + "/tmp"
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_experimental_option("prefs", {
  "download.default_directory": download_directory,
})
driver = webdriver.Chrome(options=options)

# Firefoxを利用する場合
# options = webdriver.FirefoxOptions()
# options.add_argument("-headless")
# options.set_preference("browser.download.folderList", 2)
# options.set_preference("browser.download.dir", download_directory)
# service = webdriver.FirefoxService()
# driver = webdriver.Firefox(service=service, options=options)

sbi = SBI(driver=driver).login("<ユーザID>", "<パスワード>")
hist = sbi.get_transaction_history(
  "7654321",
  date(2023, 12, 1),
  date(2023, 12, 31),
  download_directory=download_directory,
  currency=CurrencyType.jpy,
  account_name=AccountName.Representative # 代表口座
)
hist += sbi.get_transaction_history(
  "7654321",
  date(2023, 12, 1),
  date(2023, 12, 31),
  download_directory=download_directory,
  currency=CurrencyType.jpy,
  account_name=AccountName.Hybrid # ハイブリッド預金口座
)

print(f"日付, 取引内容, 金額")
for h in hist:
  print(f"{h.date}, {h.content}, {h.value}")

sbi.logout()
sbi.close()
```

### その他

#### WealthNavi

```python
from acctf.other.wealthnavi import WealthNavi
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

w = WealthNavi(driver=driver).login("<ユーザID>", "<パスワード>", "<TOTP>")
# Time-based One Time Passwordを設定していない場合
# w = WealthNavi().login("<ユーザID>", "<パスワード>")
print("資産クラス, 現在価格, 損益")
for h in w.get_valuation():
  print(f"{h.name}, {h.value}, {h.pl_value}")

w.logout()
w.close()
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
