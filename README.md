# acctf

### English | [日本語](https://github.com/hirano00o/acctf/blob/main/README.ja.md)

This is a library that obtains deposit/withdrawal history, price and quantity of held stocks from bank and securities accounts.

Currently, it supports the following.
### Securities
* SBI Securities
  * Yen-denominated
    * Stocks
      * cash/specified deposit
    * Funds
      * specified deposit
      * NISA deposit(accumulated investment limit)
      * Old accumulated NISA deposit
  * Foreign-denominated
    * Stocks(Only US)
      * cash/specified deposit

### Bank
* Mizuho Bank(Only Yen)
  * Balance
  * Transaction history
* SBI Net Bank
  * Balance(Include hybrid deposit)(Only Yen)
  * Transaction history(Include hybrid deposit)

### Other
* WealthNavi
  * Each valuation

# How to use

## Installation

```console
pip install acctf
```

## Example

### Securities

```python
from acctf.securities.sbi import SBI

sbi = SBI().login("<ユーザID>", "<パスワード>")
stocks = sbi.get_stock_specific()
print("銘柄, 数量, 取得単価, 現在値")
for s in stocks:
  print(f"{s.name}, {s.amount}, {s.acquisition_value}, {s.current_value}")

sbi.close()
```

```console
銘柄, 数量, 取得単価, 現在値
0000 銘柄1, 1000, 1234, 2345
1111 銘柄2, 1500, 789, 987
2222 銘柄3, 2000, 3450, 3456
```

### Bank

#### Balance

```python
from acctf.bank.mizuho import Mizuho

mizuho = Mizuho().login("<ユーザID>", "<パスワード>")
b = mizuho.get_balance("7654321")
print(f"口座番号, 店舗, 残高, 口座タイプ")
print(f"{b[0].account_number}, {b[0].branch_name}, {b[0].value}, {b[0].deposit_type}")

mizuho.close()
```

```console
口座番号, 店舗, 残高, 口座タイプ
7654321, 本店, 1234567.0, DepositType.ordinary
```

#### Transaction history

```python
from acctf.bank.mizuho import Mizuho

mizuho = Mizuho().login("<ユーザID>", "<パスワード>")
hist = mizuho.get_transaction_history("7654321")
# You can also specify the start/end date.
# hist = mizuho.get_transaction_history("7654321", date(2023, 12, 1), date(2023, 12, 31))
print(f"日付, 取引内容, 金額")
for h in hist:
  print(f"{h.date}, {h.content}, {h.value}")

mizuho.close()
```

```console
日付, 取引内容, 金額
2023-12-01, ＡＴＭ引き出し, -10000.0
2024-12-20, 給与, 200000.0
```

### Other

#### WealthNavi

```python
from acctf.other.wealthnavi import WealthNavi

w = WealthNavi().login("<ユーザID>", "<パスワード>", "<ワンタイムパスワード>")
# If you don't set the One Time Password
# w = WealthNavi().login("<ユーザID>", "<パスワード>")
print("資産クラス, 現在価格, 損益")
for h in w.get_valuation():
  print(f"{h.name}, {h.value}, {h.pl_value}")

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
