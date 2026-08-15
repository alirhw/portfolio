import pytest
from django.db.models import ProtectedError

from apps.portfolio.models import Skill, SkillCategory, Technology


@pytest.mark.django_db
def test_skill_category_can_be_created():
    category = SkillCategory.objects.create(
        name_en="Backend",
        name_fa="بک‌اند",
        order=1,
    )
    assert category.pk is not None
    assert str(category) == "Backend"


@pytest.mark.django_db
def test_skill_belongs_to_category_and_reverse_relation():
    category = SkillCategory.objects.create(
        name_en="Backend",
        name_fa="بک‌اند",
    )
    skill = Skill.objects.create(
        name_en="Django",
        name_fa="جنگو",
        category=category,
        proficiency=Skill.Proficiency.EXPERT,
        highlight=True,
        order=1,
    )

    assert skill.category == category
    assert str(skill) == "Django"
    assert category.skills.count() == 1
    assert category.skills.first() == skill


@pytest.mark.django_db
def test_skill_highlight_defaults_to_false():
    category = SkillCategory.objects.create(
        name_en="DevOps",
        name_fa="دواپس",
    )
    skill = Skill.objects.create(
        name_en="Docker",
        name_fa="داکر",
        category=category,
    )
    assert skill.highlight is False
    assert skill.proficiency == Skill.Proficiency.INTERMEDIATE


@pytest.mark.django_db
def test_skills_can_have_custom_order():
    category = SkillCategory.objects.create(
        name_en="Languages",
        name_fa="زبان‌ها",
    )
    skill_2 = Skill.objects.create(
        name_en="Django",
        name_fa="جنگو",
        category=category,
        order=2,
    )
    skill_1 = Skill.objects.create(
        name_en="Python",
        name_fa="پایتون",
        category=category,
        order=1,
    )

    ordered_skills = list(Skill.objects.filter(category=category))
    assert ordered_skills == [skill_1, skill_2]


@pytest.mark.django_db
def test_skill_category_deletion_is_protected():
    category = SkillCategory.objects.create(
        name_en="Frontend",
        name_fa="فرانت‌اند",
    )
    Skill.objects.create(
        name_en="HTML/CSS",
        name_fa="اچ‌تی‌ام‌ال/سی‌اس‌اس",
        category=category,
    )
    with pytest.raises(ProtectedError):
        category.delete()


@pytest.mark.django_db
def test_technology_creation_and_unique_slug():
    tech = Technology.objects.create(
        name="PostgreSQL",
        slug="postgresql",
        icon="devicon-postgresql-plain",
    )
    assert tech.pk is not None
    assert str(tech) == "PostgreSQL"
