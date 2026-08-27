# استراتژی پشتیبان‌گیری و بازیابی پایگاه داده (Database Backup & Disaster Recovery Strategy)

این سند استراتژی، زمان‌بندی، فشرده‌سازی، نگهداری و رویه بازیابی پایگاه داده PostgreSQL در پلتفرم Railway را مشخص می‌کند.

---

## ۱. معماری و استراتژی پشتیبان‌گیری

1. **پشتیبان‌گیری منطقی خودکار (Logical Backups)**:
   - اجرای اسکریپت `scripts/db_backup.sh` جهت تهیه دامپ ساختار و داده‌ها با دستور `pg_dump`.
   - فشرده‌سازی آنی با الگوریتم `gzip` جهت بهینه‌سازی فضای ذخیره‌سازی.
   - پاکسازی خودکار نسخه‌های قدیمی‌تر از ۳۰ روز بر اساس خط‌مشی نگهداری (Retention Policy).

2. **پشتیبان‌گیری بومی پلتفرم Railway (Continuous Snapshot / WAL)**:
   - پلتفرم Railway به صورت پیش‌فرض از سرویس PostgreSQL بکاپ‌های روزانه و Point-in-Time Recovery تهیه می‌کند.

---

## ۲. متغیرهای پیکربندی

| متغیر | مقدار پیش‌فرض | توضیحات |
| :--- | :--- | :--- |
| `DATABASE_URL` | - | آدرس رشته اتصال به پایگاه داده PostgreSQL |
| `BACKUP_STORAGE_PATH` | `/app/backups` | مسیر ذخیره‌سازی فایل‌های فشرده پشتیبان |

---

## ۳. فرآیند بازیابی داده‌ها (Disaster Recovery & Restore Procedure)

در صورت نیاز به بازگردانی پایگاه داده از یکی از فایل‌های پشتیبان:

```bash
# ۱. غیرفشرده‌سازی و بازیابی مستقیم به دیتابیس مقصد
gunzip -c /app/backups/portfolio_db_backup_YYYYMMDD_HHMMSS.sql.gz | psql "${DATABASE_URL}"

# ۲. اعتبارسنجی اجرای میگریشن‌ها پس از بازیابی
uv run python manage.py migrate --check
```
