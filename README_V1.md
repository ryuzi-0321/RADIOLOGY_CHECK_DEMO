# Ver.1.0 院内試用版

## 更新
既存の `db.sqlite3`、`.venv`、`media/` は残して上書きします。

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

## バックアップ
```powershell
python manage.py backup_app
```
`backups/` にDBと添付写真をまとめたZIPを作成します。

## GitHubへ上げないもの
`.venv/`, `db.sqlite3`, `media/`, `.env`, `staticfiles/`, `backups/`

## PythonAnywhere
Bashで:
```bash
git clone <GitHubリポジトリURL>
cd <リポジトリ>
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

本番では環境変数を設定:
- `DJANGO_SECRET_KEY` = 長いランダム文字列
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=ユーザー名.pythonanywhere.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://ユーザー名.pythonanywhere.com`

PythonAnywhere Static files:
- `/static/` → `<project>/staticfiles`
- `/media/` → `<project>/media`

院内試用では患者名、患者ID、検査画像など個人を特定できる情報を登録しないでください。施設の情報セキュリティ規程・承認手続きも確認してください。
