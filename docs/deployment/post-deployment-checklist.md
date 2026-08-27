# چک‌لیست و راهنمای اعتبارسنجی پس از استقرار (Post-Deployment Verification Checklist)

این سند مراحل ممیزی سلامت سرور، اعتبارسنجی اندپوینت‌های عمومی و اجرای آزمون‌های دود (Smoke Test) پس از استقرار نهایی در پلتفرم Railway را تشریح می‌کند.

---

## ۱. مانیتورینگ لاگ‌های اولیه راه‌اندازی (Container Startup Logs)

در تب **Deployments > View Logs** سرویس وب در داشبورد Railway، اطمینان حاصل کنید که مراحل زیر بدون خطا انجام شده باشند:

```text
========================================================================
RUNNING PRODUCTION PRE-FLIGHT DATABASE & STORAGE VERIFICATION
========================================================================
--> [1/3] Checking Production Database connectivity...
[OK] Database connection verified successfully.
--> [2/3] Applying pending database migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, portfolio, contact
Running migrations:
  No migrations to apply.
[OK] Database migrations applied successfully.
--> [3/3] Verifying Railway Persistent Volume write access at /app/media...
[OK] Persistent volume at '/app/media' is writable and healthy.
========================================================================
[OK] PRE-FLIGHT CHECKS PASSED: READY TO SERVE TRAFFIC
========================================================================
==> Starting Gunicorn Application Server...
[INFO] Starting gunicorn 22.x.x
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: ...
```

---

## ۲. اجرای تست دود زنده روی دامنه نهایی

با استفاده از اسکریپت `scripts/live_smoke_test.py` می‌توانید وضعیت سرور را از بیرون شبکه مورد آزمایش قرار دهید:

```bash
# نمونه اجرا روی دامنه عمومی اپلیکیشن
python scripts/live_smoke_test.py https://portfolio.alirhw.dev
```

### خروجی استاندارد مورد انتظار:
```text
========================================================================
INITIATING LIVE PRODUCTION HEALTH AUDIT: https://portfolio.alirhw.dev
========================================================================
[OK] [200] System Health Probe -> https://portfolio.alirhw.dev/healthz/
   --> Database connection and Cache confirmed operational.
[OK] [200] English Homepage -> https://portfolio.alirhw.dev/en/
[OK] [200] Persian Homepage (RTL) -> https://portfolio.alirhw.dev/fa/
[OK] [200] Robots Metadata -> https://portfolio.alirhw.dev/robots.txt
[OK] [200] Sitemap XML -> https://portfolio.alirhw.dev/sitemap.xml
========================================================================
[OK] LIVE PRODUCTION DEPLOYMENT FULLY OPERATIONAL (ZERO DOWNTIME)
========================================================================
```

---

## ۳. چک‌لیست کنترل کیفیت نهایی (Quality Gate)

- [ ] **پروب سلامت (`/healthz/`)**: بازگرداندن پاسخ `200 OK` به همراه وضعیت دیتابیس و کش.
- [ ] **گواهی SSL/TLS و هدایت امنیتی**: بارگذاری ایمن با پروتکل `https://` و فعال بودن هدرهای HSTS و CSP.
- [ ] **پایداری فایل‌های استاتیک و مدیا**: بارگذاری صحیح استایل‌ها توسط WhiteNoise با هدر کش `Cache-Control: max-age=31536000, immutable`.
- [ ] **قابلیت چندزبانه (i18n & RTL)**: بررسی رندر صحیح صفحات انگلیسی (`/en/`) و فارسی راست‌به‌چپ (`/fa/`).
- [ ] **ارسال فرم تماس و ترنستایل**: عملکرد بدون خطای ارسال پیام در بخش ارتباط با من.
