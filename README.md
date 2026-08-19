# 放射線科 点検管理（試作版）

How to CTとは別に作成した、Django製の始業点検Webアプリです。

## 主な機能

- ログイン
- CT室・MRI室・一般撮影室・透視室のサンプル点検表
- 本日の完了・未実施・異常件数
- 点検項目のチェックと項目メモ
- 異常内容・対応内容
- 履歴検索
- Excel出力
- Django管理画面から装置・点検表・項目を編集

患者名、患者IDなどの患者情報を入力する用途では使用しないでください。

## Windows / VS Codeで起動

PowerShellでプロジェクトフォルダへ移動し、以下を実行します。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

ブラウザで以下を開きます。

- アプリ: http://127.0.0.1:8000/
- 管理画面: http://127.0.0.1:8000/admin/

## GitHubへ登録

```powershell
git init
git add .
git commit -m "Initial radiology inspection prototype"
git branch -M main
git remote add origin GitHubリポジトリURL
git push -u origin main
```

`db.sqlite3`、`.venv`、秘密鍵は `.gitignore` によりGitHubへ登録されません。

## PythonAnywhereへの配置例

Bashコンソールで実行します。`ユーザー名`とリポジトリURLは置き換えてください。

```bash
cd ~
git clone GitHubリポジトリURL radiology-check
cd ~/radiology-check
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py collectstatic --noinput
```

Webタブで次を設定します。

- Source code: `/home/ユーザー名/radiology-check`
- Working directory: `/home/ユーザー名/radiology-check`
- Virtualenv: `/home/ユーザー名/radiology-check/.venv`

WSGI設定ファイルは、既存内容を整理して次の形にします。

```python
import os
import sys

project_home = '/home/ユーザー名/radiology-check'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'ユーザー名.pythonanywhere.com'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://ユーザー名.pythonanywhere.com'
os.environ['DJANGO_SECRET_KEY'] = '十分に長いランダム文字列'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Static files:

- URL: `/static/`
- Directory: `/home/ユーザー名/radiology-check/staticfiles`

設定後、WebタブのReloadを押します。

## 最初に変更する場所

管理画面 `/admin/` で以下を変更できます。

1. 「装置」で部屋・装置名を編集
2. 「点検表」で点検項目を追加・削除・並べ替え
3. 「ユーザー」でスタッフ用アカウントを追加

通常スタッフには `staff status` を付けず、管理者だけに付ける運用がおすすめです。

## 注意

- 試作版はSQLiteです。同時入力が増える本運用ではMySQL等を検討してください。
- 1つの点検表につき1日1記録です。保存後は同じ画面から修正できます。
- 医療情報システムとしての安全性・監査要件を満たすものではありません。

## Ver. 0.2 追加機能

管理者ユーザーは、画面上部の「設定」から次を操作できます。

- 装置・部屋の追加、編集、削除、使用停止
- 点検表の追加、編集、削除、使用停止
- 点検項目の追加、編集、削除
- 点検項目の表示順と必須・任意の設定

過去の点検履歴で使用されているデータは、履歴を壊さないため削除できません。使用を終了する場合は「使用中」をOFFにしてください。

既存のVer. 0.1から更新する場合、モデル変更はないためマイグレーション追加はありません。ファイルを上書き後、サーバーを再起動してください。

## Ver.0.3 更新内容

- ダッシュボードの装置カードを状態別に色分け
- 未実施・正常・異常をアイコンで表示
- 点検記録の詳細画面へのリンクを追加
- 最近の異常記録をトップ画面に最大5件表示
- スマートフォン表示を調整

データベース構造の変更はありません。更新時のマイグレーションは不要です。

## Ver.0.4: 実施曜日の設定

点検表ごとに実施曜日を設定できます。設定した曜日だけトップ画面に表示されます。
更新後は必ず次を実行してください。

```bash
python manage.py migrate
```

## Ver.0.8 集計機能
上部メニューの「集計」から、期間と装置を指定して実施率、未実施、異常件数、装置別状況、異常項目ランキング、月別推移を確認できます。集計内容はExcel出力できます。
