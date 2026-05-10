# acctf example: WealthNavi on Docker (arm64対応)

acctf を Docker コンテナで動かすサンプルです。WealthNavi の資産情報を取得します。

`mcr.microsoft.com/playwright/python` 公式イメージは linux/amd64 / linux/arm64 の multi-arch ビルドを提供しているため、Raspberry Pi 5 などの arm64 環境でもそのまま動作します。

## 構成

```
examples/
├── Dockerfile        # uv ベースの Dockerfile
├── .dockerignore
├── pyproject.toml    # acctf を依存として記載
├── main.py           # WealthNavi の get_valuation() を呼ぶサンプル
└── README.md
```

## ビルド

```console
cd examples
docker build --platform linux/arm64 -t acctf-example .
```

x86_64 環境で動かす場合は `--platform linux/amd64` を指定してください。

> **注**: このサンプルは PyPI に公開された acctf を取得します。PyPI 未公開の開発版 (本リポジトリの `main` ブランチなど) を使いたい場合は、`pyproject.toml` の `acctf` 依存を git URL に書き換えてください。書き換え方は [開発版を使う場合](#開発版を使う場合) を参照。

## 実行

認証情報は環境変数で渡します。

```console
docker run --rm --platform linux/arm64 \
  -e ACCTF_USER_ID="<ユーザID>" \
  -e ACCTF_PASSWORD="<パスワード>" \
  -e ACCTF_TOTP="<TOTPシークレット>" \
  acctf-example
```

| 環境変数 | 必須 | 説明 |
|---|---|---|
| `ACCTF_USER_ID` | ✓ | WealthNavi のユーザID |
| `ACCTF_PASSWORD` | ✓ | WealthNavi のパスワード |
| `ACCTF_TOTP` |  | 二段階認証を設定している場合の TOTP シークレット |

## 開発版を使う場合

PyPI に公開されていない開発版を試す場合は、`pyproject.toml` の依存を git URL に書き換えてください。

```toml
dependencies = [
    # 任意のブランチを指定
    "acctf @ git+https://github.com/hirano00o/acctf.git@main",
    # または特定のタグ
    # "acctf @ git+https://github.com/hirano00o/acctf.git@v0.6.0",
]
```

## 他のサービスのサンプル

SBI証券 / 住信SBIネット銀行 / みずほ銀行 のサンプルコードはリポジトリルートの [`README.md`](../README.md) を参照してください。`main.py` の `WealthNavi` 呼び出し部分をそれぞれのスクレイパーに差し替えれば同様に動作します。
