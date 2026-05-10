"""acctf を Docker コンテナで動かすサンプルスクリプト。

WealthNavi の資産情報を取得して標準出力に表示します。認証情報は環境変数で注入します。
他のサービス (SBI証券・住信SBIネット銀行・みずほ銀行) のサンプルはリポジトリルートの
README.md を参照してください。
"""
import os

from playwright.sync_api import sync_playwright

from acctf.other.wealthnavi import WealthNavi


def main() -> None:
    user_id = os.environ["ACCTF_USER_ID"]
    password = os.environ["ACCTF_PASSWORD"]
    totp = os.environ.get("ACCTF_TOTP")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        try:
            w = WealthNavi(page=page).login(user_id, password, totp)
            print("資産クラス, 現在価格, 損益")
            for asset in w.get_valuation():
                print(f"{asset.name}, {asset.value}, {asset.pl_value}")
            w.logout()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
