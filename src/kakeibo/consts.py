# 現在時刻からここで指定した日時以内のデータを取得して書き込む
EXCLUDE_DAYS = 0
EXCLUDE_MINUTES = 10

# スプレッドシートに挿入する行のテンプレート
# NOTE: このリストの最後の要素に `{{timestamp}},{{text}}` を追加すること
INSERT_ROWS_TEMPLATE = [
    "=INDEX(B:B, ROW(), 1) / 86400  + date(1970,1,1)",
    '=SPLIT(SUBSTITUTE(INDEX(I:I, ROW(), 1), "リマインダー : ", ""), ",", TRUE, TRUE)',
    "",
    "",
    "",
    '=SWITCH(INDEX(E:E, ROW(), 1), 1, INDEX(D:D, ROW(), 1)/2, 2, INDEX(D:D, ROW(), 1)/1, 3, 0, 4, INDEX(D:D, ROW(), 1)/2, 5, 0, 6, INDEX(D:D, ROW(), 1)/1, "E列が不正な値です")',
    '=SWITCH(INDEX(E:E, ROW(), 1), 1, INDEX(D:D, ROW(), 1)/2, 2, 0, 3, INDEX(D:D, ROW(), 1)/1, 4, INDEX(D:D, ROW(), 1)/2, 5, INDEX(D:D, ROW(), 1)/1, 6, 0, "E列が不正な値です")',
    '=SWITCH(INDEX(E:E, ROW(), 1), 1, INDEX(D:D, ROW(), 1)/2, 2, 0, 3, INDEX(D:D, ROW(), 1)/1, 4, -1 * INDEX(D:D, ROW(), 1)/2, 5, 0, 6, -1 * INDEX(D:D, ROW(), 1)/1, "E列が不正な値です")',
    # {{timestamp}},{{text}},
]
