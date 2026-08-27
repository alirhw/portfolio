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
    help = "Seed database with real profile and portfolio data for Ali Rouhani"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing portfolio and contact data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
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
        PortfolioProfile.objects.update_or_create(
            singleton_key=1,
            defaults={
                "full_name_en": "Ali Rouhani",
                "full_name_fa": "علی روحانی",
                "headline_en": "Software Engineer & Python/Django Developer",
                "headline_fa": "مهندس نرم‌افزار و توسعه‌دهنده پایتون و جنگو",
                "bio_en": (
                    "Senior computer engineering student and backend developer focusing on "
                    "Python, Django, and scalable web solutions. Passionate about building "
                    "robust backend architectures, working with Linux environments, and "
                    "exploring AI applications. Continuously learning modern technologies "
                    "and building practical engineering projects."
                ),
                "bio_fa": (
                    "دانشجوی سال آخر مهندسی کامپیوتر و توسعه‌دهنده بک‌اند با تمرکز بر پایتون، "
                    "جنگو و ساخت سیستم‌های وب پایدار. علاقه‌مند به معماری بک‌اند، محیط‌های لینوکسی "
                    "و کاوش در کاربردهای هوش مصنوعی. همواره در حال یادگیری فناوری‌های نوین و "
                    "پیاده‌سازی پروژه‌های کاربردی مهندسی."
                ),
                "available_for_hire": True,
                "github_url": "https://github.com/alirhw",
                "linkedin_url": "https://www.linkedin.com/in/ali-rouhani-09b45a415",
                "email": "ali.rouhani.2005@gmail.com",
            },
        )

        self.stdout.write("Seeding Technologies...")
        tech_data = [
            ("Python", "python", "code"),
            ("Django", "django", "server"),
            ("PostgreSQL", "postgresql", "database"),
            ("SQLite", "sqlite", "database"),
            ("Redis", "redis", "layers"),
            ("Docker", "docker", "container"),
            ("Linux", "linux", "terminal"),
            ("Git", "git", "git-branch"),
            ("HTML5/CSS3", "html-css", "layout"),
            ("JavaScript", "javascript", "code"),
            ("Java", "java", "cpu"),
            ("AI & LLMs", "ai-llms", "bot"),
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
                    ("Django", "جنگو", Skill.Proficiency.ADVANCED, True, 2),
                    ("RESTful APIs", "وب‌سرویس‌های REST", Skill.Proficiency.ADVANCED, True, 3),
                    ("Java", "جاوا", Skill.Proficiency.INTERMEDIATE, False, 4),
                ],
            },
            {
                "name_en": "Databases & Caching",
                "name_fa": "پایگاه‌داده و کشینگ",
                "order": 2,
                "skills": [
                    ("PostgreSQL", "پستگرس‌کیواِل", Skill.Proficiency.ADVANCED, True, 1),
                    ("SQLite", "اس‌کیوال‌لایت", Skill.Proficiency.ADVANCED, False, 2),
                    ("Redis", "ردیس", Skill.Proficiency.INTERMEDIATE, True, 3),
                    ("Database Design", "طراحی پایگاه‌داده", Skill.Proficiency.ADVANCED, False, 4),
                ],
            },
            {
                "name_en": "DevOps & Systems",
                "name_fa": "دواپس و سیستم‌ها",
                "order": 3,
                "skills": [
                    ("Linux", "لینوکس", Skill.Proficiency.INTERMEDIATE, True, 1),
                    ("Git & GitHub", "گیت و گیت‌هاب", Skill.Proficiency.ADVANCED, True, 2),
                    ("Docker", "داکر", Skill.Proficiency.INTERMEDIATE, True, 3),
                    (
                        "CI/CD Automation",
                        "پایپلاین‌های CI/CD",
                        Skill.Proficiency.INTERMEDIATE,
                        False,
                        4,
                    ),
                ],
            },
            {
                "name_en": "AI & Web Technologies",
                "name_fa": "هوش مصنوعی و وب",
                "order": 4,
                "skills": [
                    (
                        "AI & LLM Integration",
                        "هوش مصنوعی و مدل‌های زبانی",
                        Skill.Proficiency.INTERMEDIATE,
                        True,
                        1,
                    ),
                    ("HTML5 / CSS3", "HTML5 و CSS3", Skill.Proficiency.INTERMEDIATE, False, 2),
                    (
                        "JavaScript (Vanilla)",
                        "جاوا اسکریپت",
                        Skill.Proficiency.INTERMEDIATE,
                        False,
                        3,
                    ),
                ],
            },
        ]

        for cat_data in categories:
            cat, _ = SkillCategory.objects.update_or_create(
                name_en=cat_data["name_en"],
                defaults={
                    "name_fa": cat_data["name_fa"],
                    "order": cat_data["order"],
                },
            )
            for s_name_en, s_name_fa, s_prof, s_highlight, s_order in cat_data["skills"]:
                Skill.objects.update_or_create(
                    name_en=s_name_en,
                    category=cat,
                    defaults={
                        "name_fa": s_name_fa,
                        "proficiency": s_prof,
                        "highlight": s_highlight,
                        "order": s_order,
                    },
                )

        self.stdout.write("Seeding Currently Building...")
        CurrentlyBuilding.objects.update_or_create(
            id=1,
            defaults={
                "title_en": "I Got You — AI Assistant for Junior Developers",
                "title_fa": "I Got You — دستیار هوش مصنوعی برای برنامه‌نویسان",
                "description_en": (
                    "An intelligent AI-driven chatbot designed to mentor junior developers, "
                    "debug code, and provide structured learning pathways."
                ),
                "description_fa": (
                    "چت‌بات هوشمند مبتنی بر هوش مصنوعی برای راهنمایی، رفع باگ و ارائه "
                    "مسیر یادگیری برای توسعه‌دهندگان تازه‌کار."
                ),
                "current_phase_en": "Architecture & MVP",
                "current_phase_fa": "معماری و توسعه MVP",
                "progress_percentage": 65,
                "related_link": "https://github.com/alirhw",
                "is_active": True,
            },
        )

        self.stdout.write("Seeding Projects...")
        projects_data = [
            {
                "title_en": "Modular Developer Portfolio & Interactive Terminal",
                "title_fa": "پورتفولیوی ماژولار توسعه‌دهنده با ترمینال تعاملی",
                "slug": "developer-portfolio",
                "description_en": (
                    "Production-ready bilingual developer portfolio platform built with Django 6, "
                    "progressive enhancement interactive web terminal with Tab autocomplete, "
                    "WhiteNoise asset caching, and Docker CI/CD."
                ),
                "description_fa": (
                    "وب‌اپلیکیشن پروداکشن پورتفولیوی دوزبانه (فارسی و انگلیسی) توسعه‌یافته با "
                    "جنگو ۶، ترمینال تعاملی جاوا اسکریپت با پشتیبانی از Autocomplete و کلید Tab، "
                    "مانیتورینگ Sentry و استقرار کانتینری داکر."
                ),
                "is_featured": True,
                "is_published": True,
                "order": 1,
                "repository_url": "https://github.com/alirhw/portfolio",
                "demo_url": "https://portfolio.alirhw.dev",
                "techs": ["python", "django", "postgresql", "docker", "html-css", "javascript"],
            },
            {
                "title_en": "Auto Spare Parts E-Commerce Platform",
                "title_fa": "سامانه فروشگاهی آنلاین لوازم یدکی خودرو",
                "slug": "autoparts-ecommerce",
                "description_en": (
                    "Comprehensive automotive spare parts e-commerce platform providing "
                    "structured catalog management, vehicle model compatibility search, "
                    "secure user authentication, and shopping cart order processing."
                ),
                "description_fa": (
                    "پلتفرم فروشگاهی جامع قطعات خودرو با قابلیت دسته‌بندی تخصصی قطعات یدکی، "
                    "جستجوی سازگاری با مدل خودرو، مدیریت سبد خرید و کاتالوگ محصولات."
                ),
                "is_featured": True,
                "is_published": True,
                "order": 2,
                "repository_url": "https://github.com/alirhw",
                "demo_url": "",
                "techs": ["python", "django", "postgresql", "html-css", "javascript"],
            },
            {
                "title_en": "I Got You — AI Developer Assistant",
                "title_fa": "دستیار هوش مصنوعی توسعه‌دهندگان (I Got You)",
                "slug": "i-got-you-ai",
                "description_en": (
                    "Conversational AI tool integrating modern language models to provide "
                    "contextual coding explanations, syntax error resolution, and interactive "
                    "guided examples tailored for junior software developers."
                ),
                "description_fa": (
                    "ابزار هوش مصنوعی مکالمه‌محور برای ارائه توضیحات مفهومی کد، خطایابی "
                    "سریع ساختار پایتون و ارائه مثال‌های کاربردی به برنامه‌نویسان تازه‌کار."
                ),
                "is_featured": True,
                "is_published": True,
                "order": 3,
                "repository_url": "https://github.com/alirhw",
                "demo_url": "",
                "techs": ["python", "ai-llms", "django"],
            },
        ]

        for p_data in projects_data:
            tech_slugs = p_data.pop("techs")
            proj, _ = Project.objects.update_or_create(
                slug=p_data["slug"],
                defaults=p_data,
            )
            proj.technologies.set([tech_map[ts] for ts in tech_slugs if ts in tech_map])

        self.stdout.write("Seeding Experience...")
        Experience.objects.update_or_create(
            company="Independent Software Projects & Freelance",
            position_en="Independent Software Developer & Backend Engineer",
            defaults={
                "position_fa": "توسعه‌دهنده پروژه‌های مستقل نرم‌افزاری و بک‌اند",
                "start_date": date(2023, 1, 1),
                "is_current": True,
                "description_en": (
                    "Designed and developed backend services and web applications using Python "
                    "and Django. Implemented relational database schemas, REST APIs, "
                    "and integrated external services and AI tools."
                ),
                "description_fa": (
                    "طراحی و توسعه سرویس‌های وب و بک‌اند با استفاده از پایتون و جنگو. پیاده‌سازی "
                    "ساختار پایگاه‌داده‌های رابطه‌ای، وب‌سرویس‌های REST و یکپارچه‌سازی با سرویس‌های "
                    "خارجی و ابزارهای هوش مصنوعی."
                ),
                "order": 1,
            },
        )

        Experience.objects.update_or_create(
            company="Computer Engineering Department",
            position_en="Software Engineering Student Project Lead",
            defaults={
                "position_fa": "توسعه‌دهنده پروژه‌های دانشگاهی و تحقیقاتی",
                "start_date": date(2022, 9, 1),
                "end_date": date(2024, 6, 1),
                "is_current": False,
                "description_en": (
                    "Collaborated on software engineering course projects, implementing "
                    "algorithms, database systems, object-oriented software in Python and Java, "
                    "and exploring Linux workflows."
                ),
                "description_fa": (
                    "پیاده‌سازی پروژه‌های درسی مهندسی نرم‌افزار، الگوریتم‌ها و ساختار داده، "
                    "برنامه‌نویسی شیءگرا با پایتون و جاوا و کار با ابزارها و محیط‌های لینوکسی."
                ),
                "order": 2,
            },
        )

        self.stdout.write("Seeding Education...")
        Education.objects.update_or_create(
            degree_en="B.Sc. in Computer Engineering",
            institution_en="University",
            defaults={
                "degree_fa": "کارشناسی مهندسی کامپیوتر",
                "institution_fa": "دانشگاه",
                "field_of_study_en": "Software Engineering",
                "field_of_study_fa": "مهندسی نرم‌افزار",
                "start_year": 2021,
                "graduation_year": 2025,
                "description_en": (
                    "Focusing on software development methodologies, database systems, computer "
                    "networks, algorithms, and artificial intelligence."
                ),
                "description_fa": (
                    "تمرکز بر مهندسی نرم‌افزار، طراحی سیستم‌های پایگاه‌داده، شبکه‌های کامپیوتری، "
                    "الگوریتم‌ها و هوش مصنوعی."
                ),
                "order": 1,
            },
        )

        self.stdout.write(
            self.style.SUCCESS("Database seeded successfully with real developer profile!")
        )
