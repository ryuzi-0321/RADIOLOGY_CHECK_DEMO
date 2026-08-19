from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from datetime import datetime
import zipfile

class Command(BaseCommand):
    help = "Back up db.sqlite3 and uploaded media."
    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        dest = base / "backups"
        dest.mkdir(exist_ok=True)
        out = dest / ("workcheck_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".zip")
        db = base / "db.sqlite3"
        media = Path(settings.MEDIA_ROOT)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            if db.exists(): z.write(db, "db.sqlite3")
            if media.exists():
                for f in media.rglob("*"):
                    if f.is_file(): z.write(f, Path("media") / f.relative_to(media))
        self.stdout.write(self.style.SUCCESS("Backup created: " + str(out)))
