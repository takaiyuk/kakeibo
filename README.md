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
