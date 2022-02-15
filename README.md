# kakeibo

以下を毎日0時に実行する

1. Slack API を利用して Slack メッセージを取得する
2. 前日分のみに絞る
3. IFTTT の Webhook URL を利用して Google Sheet に行を追加する

## Execute

```
$ cp .env.example .env
$ python src/main.py
```

## Lambda

AWS Lambda で定期実行するためには requests ライブラリを含んだ Layer を作成する

Linux 開発マシンを使用してこれらのライブラリをコンパイルしてビルドし、バイナリを Amazon Linux と互換性を持たせる必要がある（[ref.](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-layers.html)）

```
$ mkdir python
$ pip install -t python requests
$ zip -r9 layer.zip python
$ rm -r python
```
