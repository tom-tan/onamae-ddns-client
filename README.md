# これなに？

お名前.com 用のダイナミックDNSクライアントです(非公式)。

## 実行環境
- Python 2.7.18
  - 外部ライブラリは利用していません。

## 使い方

```console
$ cat .env
USERID=<your user id>
PASSWORD=<your password>
HOSTNAME=<your hostname>
DOMNAME=<your domain name>
$ ./onamae-ddns-client.py
$ echo $? # 成功時には黙って 0 を返す
0
```

## 参考
- [LinuxやMacで お名前.com ダイナミックDNS の IPアドレスを更新する](https://qiita.com/ats124/items/59ec0f444d00bbcea27d)
