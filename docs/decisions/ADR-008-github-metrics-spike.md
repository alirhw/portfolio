# ADR-008: GitHub Integration Semantics and Architecture

## Context (English)
To showcase open-source activity in the portfolio, we need to fetch 6 key metrics from GitHub:
1. `total_contributions`: Total contributions in the current calendar year fetched via GraphQL API (`contributionsCollection`).
2. `public_repos_count`: Total number of active, non-fork, non-archived public repositories.
3. `total_stars_earned`: Cumulative stars earned across user-owned repositories (excluding forks).
4. `current_streak_days`: Consecutive active contribution days up to today.
5. `top_languages`: Top 3 programming languages weighted by byte count across primary repositories.
6. `followers_count`: Follower count representing open-source community engagement and reach.

## Decisions (English)
1. **Hybrid GraphQL & REST Approach**: Because fetching the Contribution Calendar and aggregating stargazer counts across non-fork repositories requires multiple roundtrips and heavy pagination with the REST API, GitHub GraphQL API is chosen as the primary protocol to fetch all required metrics in a single network query.
2. **Zero DB Migration (Cache-Only Storage)**: GitHub metrics are ephemeral external data and must not be persisted in database models. All metric values are managed strictly via the Django Cache Framework.
3. **Graceful Degradation / Safe Fallback Pattern**: In the event of network timeouts, rate limit exhaustion, or GitHub API outages, the system will seamlessly serve stale cached data or the safe fallback object `GitHubMetrics.empty()`, guaranteeing zero 500 errors or page crashes.

---

## متن فارسی (Persian Context & Decisions)

### زمینه (Context)
برای نمایش فعالیت‌های اوپن‌سورس در پورتفولیو، نیاز به واکشی ۶ متریک کلیدی از گیتهاب داریم:
1. `total_contributions`: مجموع کل مشارکت‌های سال جاری از طریق GraphQL API (`contributionsCollection`).
2. `public_repos_count`: تعداد کل مخازن عمومی فعال کاربر (بدون احتساب مخازن آرشیوشده یا فورک‌ها).
3. `total_stars_earned`: مجموع کل ستاره‌های دریافت‌شده روی مخازن اختصاصی کاربر (نه فورک‌ها).
4. `current_streak_days`: تعداد روزهای متوالی مشارکت فعال تا امروز.
5. `top_languages`: ۳ زبان برنامه‌نویسی برتر بر اساس حجم کد (Byte Count) در مخازن اصلی کاربر.
6. `followers_count`: تعداد دنبال‌کنندگان جهت نمایش اثرگذاری در جامعه اوپن‌سورس.

### تصمیمات (Decisions)
1. **استفاده ترکیبی از GraphQL و REST**: به دلیل اینکه اطلاعات Contribution Calendar و تفکیک ستاره‌های مخازن اختصاصی در REST به چندین فراخوانی و پیجینیشن سنگین نیاز دارد، GraphQL به عنوان پروتکل اصلی فراخوانی با یک درخواست منفرد (Single Query) انتخاب می‌شود.
2. **بدون مدل و دیتابیس (Zero DB Migration)**: داده‌های گیتهاب نباید در جداول دیتابیس ذخیره شوند، بلکه منحصراً از طریق کش جنگو (Django Cache Framework) مدیریت می‌شوند.
3. **الگوی Graceful Degradation / Safe Fallback**: در صورت بروز خطای شبکه، اتمام Rate Limit یا قطعی گیتهاب، سیستم از کش قبلی یا آبجکت امن `GitHubMetrics.empty()` استفاده کرده و هرگز نباید پاسخ 500 یا Crash در صفحه ایجاد کند.
