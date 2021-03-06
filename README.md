# kakeibo

Slack の特定チャンネルに送信されたメッセージを Spreadsheet に転記するもの

以下を定期実行する

1. Slack API を利用して Slack メッセージを取得する
2. 特定期間に投稿されたメッセージのみに絞る
3. IFTTT の Webhook URL を利用して Google Sheet に行を追加する

```mermaid
graph LR;
    EventBridge -- kick --> Lambda;
    Lambda -- get --> Slack
    Slack --> Lambda;
    Lambda -- post --> IFTTT;
    IFTTT --> Spreadsheet;
```

## Execute

```shell
$ cp .env.example .env
$ make run
```

### Test

```shell
$ make test
```

### Mypy

```shell
$ make mypy
```

## Lambda

AWS Lambda で定期実行するためには requests ライブラリを含んだ Layer を作成する

Linux 開発マシンを使用してこれらのライブラリをコンパイルしてビルドし、バイナリを Amazon Linux と互換性を持たせる必要がある（[ref.](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-layers.html)）

```shell
$ make lambda-layer
```
