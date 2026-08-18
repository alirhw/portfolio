from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.contact.models import ContactMessage
from apps.portfolio.models import (
    CurrentlyBuilding,
    Education,
    Experience,
    PortfolioProfile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


class Command(BaseCommand):
    help = "Seed database with rich mock data for testing portfolio sections"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing portfolio and contact data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing mock data...")
            PortfolioProfile.objects.all().delete()
            Project.objects.all().delete()
            Skill.objects.all().delete()
            SkillCategory.objects.all().delete()
            Technology.objects.all().delete()
            CurrentlyBuilding.objects.all().delete()
            Experience.objects.all().delete()
            Education.objects.all().delete()
            ContactMessage.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing data cleared."))

        self.stdout.write("Seeding Portfolio Profile...")
        profile, created = PortfolioProfile.objects.update_or_create(
            singleton_key=1,
            defaults={
                "full_name_en": "Ali Rouhani",
                "full_name_fa": "علی روحانی",
                "headline_en": "Backend Developer & AI Systems Engineer",
                "headline_fa": "توسعه‌دهنده بک‌اند و مهندس سیستم‌های هوش مصنوعی",
                "bio_en": (
                    "Passionate backend engineer with 4+ years of experience designing "
                    "scalable microservices, high-throughput asynchronous pipelines, "
                    "and AI-powered backend systems. Experienced in Python, Django, "
                    "FastAPI, Redis, Docker, and PostgreSQL."
                ),
                "bio_fa": (
                    "مهندس بک‌اند با بیش از ۴ سال تجربه در طراحی میکروسرویس‌های مقیاس‌پذیر، "
                    "پایپ‌لاین‌های ناهمگام پرسرعت و سیستم‌های هوش مصنوعی. مسلط به پایتون، "
                    "جنگو، فست‌ای‌پی‌آی، ردیس، داکر و پستگرس‌کیواِل."
                ),
                "available_for_hire": True,
                "github_url": "https://github.com/alirhw",
                "linkedin_url": "https://linkedin.com/in/alirhw",
                "email": "ali.rouhani.2005@gmail.com",
            },
        )

        self.stdout.write("Seeding Technologies...")
        tech_data = [
            ("Python", "python", "code"),
            ("Django", "django", "server"),
            ("FastAPI", "fastapi", "zap"),
            ("PostgreSQL", "postgresql", "database"),
            ("Redis", "redis", "layers"),
            ("Celery", "celery", "cpu"),
            ("Docker", "docker", "container"),
            ("LangChain", "langchain", "bot"),
            ("WebSockets", "websockets", "activity"),
            ("React", "react", "layout"),
            ("Linux", "linux", "terminal"),
            ("Git", "git", "git-branch"),
        ]
        tech_map = {}
        for name, slug, icon in tech_data:
            tech, _ = Technology.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon},
            )
            tech_map[slug] = tech

        self.stdout.write("Seeding Skill Categories and Skills...")
        categories = [
            {
                "name_en": "Backend Development",
                "name_fa": "توسعه بک‌اند",
                "order": 1,
                "skills": [
                    ("Python", "پایتون", Skill.Proficiency.EXPERT, True, 1),
                    ("Django / DRF", "جنگو و رست‌فریم‌ورک", Skill.Proficiency.EXPERT, True, 2),
                    ("FastAPI", "فست‌ای‌پی‌آی", Skill.Proficiency.ADVANCED, True, 3),
                    ("Celery & Redis", "سلری و ردیس", Skill.Proficiency.ADVANCED, True, 4),
                    (
                        "Asyncio & WebSockets",
                        "تسک‌های ناهمگام و وب‌سوکت",
                        Skill.Proficiency.ADVANCED,
                        True,
                        5,
                    ),
                    (
                        "RESTful APIs & GraphQL",
                        "طراحی API و گراف‌کیواِل",
                        Skill.Proficiency.ADVANCED,
                        True,
                        6,
                    ),
                ],
            },
            {
                "name_en": "Databases & Storage",
                "name_fa": "پایگاه‌های داده و ذخیره‌سازی",
                "order": 2,
                "skills": [
                    ("PostgreSQL", "پستگرس‌کیواِل", Skill.Proficiency.EXPERT, True, 1),
                    ("Redis Caching", "ردیس و کشینگ", Skill.Proficiency.ADVANCED, True, 2),
                    (
                        "Query Optimization & Indexing",
                        "بهینه‌سازی کوئری و ایندکس‌گذاری",
                        Skill.Proficiency.ADVANCED,
                        True,
                        3,
                    ),
                    ("SQLite", "اس‌کیولایت", Skill.Proficiency.ADVANCED, True, 4),
                    ("MongoDB", "مانگودی‌بی", Skill.Proficiency.INTERMEDIATE, True, 5),
                ],
            },
            {
                "name_en": "DevOps & Infrastructure",
                "name_fa": "دواپس و زیرساخت",
                "order": 3,
                "skills": [
                    (
                        "Docker & Docker Compose",
                        "داکر و داکر کمپوز",
                        Skill.Proficiency.ADVANCED,
                        True,
                        1,
                    ),
                    (
                        "CI/CD (GitHub Actions)",
                        "گیت‌هاب اکشنز و CI/CD",
                        Skill.Proficiency.ADVANCED,
                        True,
                        2,
                    ),
                    (
                        "Linux & Bash Scripting",
                        "لینوکس و اسکریپت‌نویسی بش",
                        Skill.Proficiency.ADVANCED,
                        True,
                        3,
                    ),
                    (
                        "Nginx & Reverse Proxies",
                        "انجین‌ایکس و پراکسی معکوس",
                        Skill.Proficiency.INTERMEDIATE,
                        True,
                        4,
                    ),
                    (
                        "Microservices Architecture",
                        "معماری میکروسرویس",
                        Skill.Proficiency.ADVANCED,
                        True,
                        5,
                    ),
                ],
            },
            {
                "name_en": "AI & Machine Learning",
                "name_fa": "هوش مصنوعی و یادگیری ماشین",
                "order": 4,
                "skills": [
                    (
                        "RAG (Retrieval-Augmented Generation)",
                        "سیستم‌های RAG و جستجوی معنایی",
                        Skill.Proficiency.ADVANCED,
                        True,
                        1,
                    ),
                    (
                        "LangChain & LlamaIndex",
                        "فریم‌ورک‌های لنگ‌چین و لاماایندکس",
                        Skill.Proficiency.ADVANCED,
                        True,
                        2,
                    ),
                    (
                        "LLM Agent Workflows",
                        "طراحی ورک‌فلوهای ایجنتی",
                        Skill.Proficiency.ADVANCED,
                        True,
                        3,
                    ),
                    (
                        "PyTorch & Transformers",
                        "پای‌تورچ و ترنسفورمرها",
                        Skill.Proficiency.INTERMEDIATE,
                        True,
                        4,
                    ),
                ],
            },
        ]

        for cat_info in categories:
            cat, _ = SkillCategory.objects.update_or_create(
                name_en=cat_info["name_en"],
                defaults={
                    "name_fa": cat_info["name_fa"],
                    "order": cat_info["order"],
                },
            )
            for name_en, name_fa, prof, highlight, order in cat_info["skills"]:
                Skill.objects.update_or_create(
                    name_en=name_en,
                    category=cat,
                    defaults={
                        "name_fa": name_fa,
                        "proficiency": prof,
                        "highlight": highlight,
                        "order": order,
                    },
                )

        self.stdout.write("Seeding Projects...")
        projects_data = [
            {
                "title_en": "CloudSync: Distributed Task Queue & Event Pipeline",
                "title_fa": "سامانه پردازش توزیع‌شده و صف وظایف CloudSync",
                "slug": "cloudsync-distributed-task-queue",
                "description_en": (
                    "A high-performance distributed task scheduler and event streaming pipeline "
                    "built with Django, Celery, Redis, and WebSockets. Handles over 10,000 "
                    "tasks/sec with sub-second latency, automated retry policies, and "
                    "real-time dashboard telemetry."
                ),
                "description_fa": (
                    "سامانه زمان‌بندی و صف وظایف توزیع‌شده با کارایی فوق‌العاده بالا با پایتون، "
                    "جنگو، سلری و ردیس. قابلیت پردازش بیش از ۱۰ هزار تسک در ثانیه به همراه "
                    "داشبورد مانیتورینگ بلادرنگ."
                ),
                "is_published": True,
                "is_featured": True,
                "demo_url": "https://github.com/alirhw/portfolio",
                "repository_url": "https://github.com/alirhw/portfolio",
                "order": 1,
                "techs": ["python", "django", "celery", "redis", "docker"],
            },
            {
                "title_en": "DocuSense: Enterprise RAG & Knowledge Engine",
                "title_fa": "موتور هوشمند جستجو و تحلیل اسناد سازمانی DocuSense",
                "slug": "docusense-enterprise-rag",
                "description_en": (
                    "Production-ready Retrieval Augmented Generation (RAG) system capable of "
                    "indexing complex multi-format document repositories. Utilizes dense vector "
                    "search, hybrid re-ranking, and streaming LLM responses with citations."
                ),
                "description_fa": (
                    "سیستم پیشرفته RAG برای ایندکس و پردازش اسناد سازمانی و پاسخ‌دهی هوشمند "
                    "به سوالات کاربران با جستجوی معنایی و ارجاع به منابع دقیق."
                ),
                "is_published": True,
                "is_featured": True,
                "demo_url": "https://github.com/alirhw/portfolio",
                "repository_url": "https://github.com/alirhw/portfolio",
                "order": 2,
                "techs": ["python", "fastapi", "langchain", "postgresql", "docker"],
            },
            {
                "title_en": "HyperPay: Resilient Multi-Gateway Payment Engine",
                "title_fa": "موتور تراکنش‌های مالی و درگاه‌های پرداخت HyperPay",
                "slug": "hyperpay-payment-gateway",
                "description_en": (
                    "Financial transaction processing microservice with robust idempotency "
                    "guarantees, distributed locking, circuit breaker patterns, automated "
                    "reconciliation jobs, and HMAC-signed webhook delivery."
                ),
                "description_fa": (
                    "میکروسرویس پردازش تراکنش‌های مالی با تضمین عدم تکرار (idempotency)، "
                    "سیستم مدارشکن (circuit breaker) و تسویه‌حساب و وب‌هوک‌های امن."
                ),
                "is_published": True,
                "is_featured": True,
                "demo_url": "https://github.com/alirhw/portfolio",
                "repository_url": "https://github.com/alirhw/portfolio",
                "order": 3,
                "techs": ["python", "django", "postgresql", "redis", "docker"],
            },
            {
                "title_en": "MetricFlow: Real-time Observability & APM Toolkit",
                "title_fa": "سیستم مانیتورینگ عملکرد و تحلیل متریک‌های لحظه‌ای MetricFlow",
                "slug": "metricflow-apm-toolkit",
                "description_en": (
                    "Lightweight application performance monitoring and telemetry aggregator "
                    "providing real-time alerts, health check probes, latency histograms, "
                    "and distributed tracing across microservices."
                ),
                "description_fa": (
                    "ابزار سبک و سریع مانیتورینگ و ارزیابی سلامت سرویس‌ها با اعلان‌های آنی، "
                    "محاسبه توزیع تاخیر و رهگیری درخواست‌ها."
                ),
                "is_published": True,
                "is_featured": False,
                "demo_url": "https://github.com/alirhw/portfolio",
                "repository_url": "https://github.com/alirhw/portfolio",
                "order": 4,
                "techs": ["python", "fastapi", "redis", "websockets"],
            },
            {
                "title_en": "NexusAuth: Zero-Trust OAuth2 & Identity Provider",
                "title_fa": "سرور مدیریت هویت و احراز هویت متمرکز NexusAuth",
                "slug": "nexus-auth-identity-provider",
                "description_en": (
                    "RFC-compliant OAuth2 and OpenID Connect identity provider with MFA, "
                    "session revocation across devices, role-based access control (RBAC), "
                    "and cryptographic JWT token signing."
                ),
                "description_fa": (
                    "سرور احراز هویت متمرکز منطبق بر استاندارد OAuth2 و OpenID با پشتیبانی "
                    "از ورود دومرحله‌ای و ابطال لحظه‌ای سشن‌ها."
                ),
                "is_published": True,
                "is_featured": False,
                "demo_url": "https://github.com/alirhw/portfolio",
                "repository_url": "https://github.com/alirhw/portfolio",
                "order": 5,
                "techs": ["python", "django", "postgresql", "redis"],
            },
        ]

        for p_data in projects_data:
            techs = [tech_map[slug] for slug in p_data["techs"] if slug in tech_map]
            proj, _ = Project.objects.update_or_create(
                slug=p_data["slug"],
                defaults={
                    "title_en": p_data["title_en"],
                    "title_fa": p_data["title_fa"],
                    "description_en": p_data["description_en"],
                    "description_fa": p_data["description_fa"],
                    "is_published": p_data["is_published"],
                    "is_featured": p_data["is_featured"],
                    "demo_url": p_data["demo_url"],
                    "repository_url": p_data["repository_url"],
                    "order": p_data["order"],
                },
            )
            proj.technologies.set(techs)

        self.stdout.write("Seeding Currently Building items...")
        building_items = [
            {
                "title_en": "Agentic Task Orchestration Framework",
                "title_fa": "فریم‌ورک ارکستراسیون خودکار ایجنت‌های هوش مصنوعی",
                "description_en": (
                    "Building a modular multi-agent workflow framework featuring sandboxed "
                    "Python code execution, stateful memory management, and self-correcting "
                    "query planners."
                ),
                "description_fa": (
                    "توسعه فریم‌ورک ماژولار ارکستراسیون چند ایجنتی با امکان اجرای امن کدها در "
                    "محیط ایزوله و مدیریت حافظه بلندمدت."
                ),
                "progress_percentage": 80,
                "current_phase_en": "Benchmarking & Security Sandboxing",
                "current_phase_fa": "ارزیابی بنچمارک و امنیت محیط ایزوله",
                "related_link": "https://github.com/alirhw",
                "is_active": True,
                "order": 1,
            },
            {
                "title_en": "High-Throughput ASGI Event Gateway",
                "title_fa": "دروازه رویدادهای ناهمگام پرسرعت بر بستر ASGI",
                "description_en": (
                    "Developing an ultra-low latency event gateway handling 50k+ persistent "
                    "concurrent WebSocket connections with backpressure management."
                ),
                "description_fa": (
                    "پیاده‌سازی گیت‌وی بلادرنگ برای اتصال بیش از ۵۰ هزار کلاینت همزمان و "
                    "کنترل هوشمند جریان داده."
                ),
                "progress_percentage": 45,
                "current_phase_en": "Concurrency Optimization & Protocol Tuning",
                "current_phase_fa": "بهینه‌سازی همزمانی و تنظیم پروتکل",
                "related_link": "https://github.com/alirhw",
                "is_active": True,
                "order": 2,
            },
        ]

        for b_data in building_items:
            CurrentlyBuilding.objects.update_or_create(
                title_en=b_data["title_en"],
                defaults=b_data,
            )

        self.stdout.write("Seeding Experience...")
        experiences = [
            {
                "position_en": "Lead Backend Engineer",
                "position_fa": "مهندس ارشد بک‌اند",
                "company": "Apex Cloud Systems",
                "company_url": "https://example.com",
                "start_date": date(2023, 6, 1),
                "end_date": None,
                "is_current": True,
                "description_en": (
                    "Spearheaded core backend architecture for high-volume enterprise SaaS. "
                    "Improved API response times by 40% through Redis caching and query "
                    "refactoring. Mentored junior backend developers."
                ),
                "description_fa": (
                    "راهبری معماری سیستم‌های بک‌اند با ترافیک بالا، کاهش ۴۰ درصدی زمان پاسخگویی "
                    "API با بهینه‌سازی دیتابیس و کشینگ ردیس."
                ),
                "order": 1,
            },
            {
                "position_en": "Python / Django Developer",
                "position_fa": "توسعه‌دهنده پایتون و جنگو",
                "company": "NovaTech Solutions",
                "company_url": "https://example.com",
                "start_date": date(2021, 9, 1),
                "end_date": date(2023, 5, 31),
                "is_current": False,
                "description_en": (
                    "Developed RESTful APIs, asynchronous Celery task pipelines, and payment "
                    "gateway integrations. Implemented automated CI/CD workflows and increased "
                    "test coverage to 95%."
                ),
                "description_fa": (
                    "توسعه APIهای مقیاس‌پذیر و صف‌های پردازش غیرهمگام با سلری، پیاده‌سازی "
                    "تست‌های اتوماتیک و اتصال به درگاه‌های بانکی."
                ),
                "order": 2,
            },
        ]

        for exp_data in experiences:
            Experience.objects.update_or_create(
                position_en=exp_data["position_en"],
                company=exp_data["company"],
                defaults=exp_data,
            )

        self.stdout.write("Seeding Education...")
        educations = [
            {
                "degree_en": "Bachelor of Science",
                "degree_fa": "کارشناسی",
                "institution_en": "University of Tehran",
                "institution_fa": "دانشگاه تهران",
                "field_of_study_en": "Computer Engineering",
                "field_of_study_fa": "مهندسی کامپیوتر",
                "start_year": 2020,
                "graduation_year": 2024,
                "description_en": (
                    "Specialized in Distributed Systems, Operating Systems, Algorithm "
                    "Design, and Relational Database Engineering."
                ),
                "description_fa": (
                    "تمرکز بر سیستم‌های توزیع‌شده، سیستم‌های عامل، طراحی الگوریتم "
                    "و مهندسی پایگاه‌داده."
                ),
                "order": 1,
            },
        ]

        for edu_data in educations:
            Education.objects.update_or_create(
                degree_en=edu_data["degree_en"],
                institution_en=edu_data["institution_en"],
                defaults=edu_data,
            )

        self.stdout.write("Seeding Sample Contact Messages...")
        messages = [
            {
                "sender_name": "Sara Ahmadi",
                "email": "sara.ahmadi@techstart.io",
                "subject": "Backend Consulting & Architecture Review",
                "message": (
                    "Hi Ali, we were really impressed by your open-source projects and would "
                    "like to discuss an advisory role for our backend infrastructure."
                ),
                "ip_address": "127.0.0.1",
                "is_read": True,
                "is_notified": True,
            },
            {
                "sender_name": "Michael Vance",
                "email": "michael.vance@innovate.ai",
                "subject": "Invitation for Senior AI/Backend Role",
                "message": (
                    "Hello Ali, we love your work on RAG pipelines and distributed queues. "
                    "Are you open to exploring senior engineering positions?"
                ),
                "ip_address": "127.0.0.1",
                "is_read": False,
                "is_notified": True,
            },
        ]

        for msg_data in messages:
            ContactMessage.objects.update_or_create(
                email=msg_data["email"],
                subject=msg_data["subject"],
                defaults=msg_data,
            )

        self.stdout.write(
            self.style.SUCCESS("[OK] Successfully seeded all mock data for portfolio & contact!")
        )
