# ADR-008: GitHub Integration Semantics and Architecture

## Context
برای نمایش فعالیت‌های اوپن‌سورس در پورتفولیو، نیاز به واکشی ۶ متریک کلیدی از گیتهاب داریم:
1. `total_contributions`: مجموع کل مشارکت‌های سال جاری از طریق GraphQL API (`contributionsCollection`).
2. `public_repos_count`: تعداد کل مخازن عمومی فعال کاربر.
3. `total_stars_earned`: مجموع کل ستاره‌های دریافت‌شده روی مخازن غیراختصاصی/اختصاصی کاربر.
4. `current_streak_days`: تعداد روزهای متوالی مشارکت فعال.
5. `top_languages`: ۳ زبان برنامه‌نویسی برتر بر اساس حجم کد در مخازن اصلی کاربر.
6. `followers_count`: تعداد دنبال‌کنندگان جهت نمایش اثرگذاری در جامعه اوپن‌سورس.

## Decisions
1. **استفاده ترکیبی از GraphQL و REST**: به دلیل اینکه اطلاعات Contribution Calendar و تفکیک ستاره‌های مخازن اختصاصی در REST به چندین فراخوانی و پیجینیشن سنگین نیاز دارد، GraphQL به عنوان پروتکل اصلی فراخوانی با یک درخواست منفرد (Single Query) انتخاب می‌شود.
2. **بدون مدل و دیتابیس (Zero DB Migration)**: داده‌های گیتهاب نباید در جداول دیتابیس ذخیره شوند، بلکه منحصراً از طریق کش جنگو (Django Cache Framework) مدیریت می‌شوند.
3. **الگوی Graceful Degradation / Safe Fallback**: در صورت بروز خطای شبکه، اتمام Rate Limit یا قطعی گیتهاب، سیستم از کش قبلی یا آبجکت امن `GitHubMetrics.empty()` استفاده کرده و هرگز نباید پاسخ 500 یا Crash در صفحه ایجاد کند.
