# account scraper

This is a library that obtains deposit/withdrawal history, price and quantity of held stocks from bank and securities accounts.

Currently, it supports the following.
* SBI Securities
  * Yen-denominated
    * Stocks
      * cash/specified deposit
    * Funds
      * specified deposit
      * NISA deposit(accumulated investment limit)
      * Old accumulated NISA deposit

# How to use

## Installation

```console
pip install git+ssh://git@github.com/hirano00o/account-scraper.git
```

## Example

```python
from securities.sbi import SBI

sbi = SBI().login("<ユーザID>", "<パスワード>")
stocks = sbi.get_stock_specific()
print(f"銘柄, 数量, 取得単価, 現在値")
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
