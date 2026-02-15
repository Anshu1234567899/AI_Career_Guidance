from django.contrib import admin
from .models import (
    Skill,
    StudentProfile,
    Career,
    CareerQuizQuestion,
    CareerQuizOption,
    CareerQuizResult,
    Category
)


# =========================
# Basic Models
# =========================
admin.site.register(Skill)
admin.site.register(StudentProfile)


# =========================
# Category Admin
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# =========================
# Career Admin
# =========================
@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "average_salary")
    list_filter = ("category",)
    search_fields = ("name",)

    fields = (
        "name",
        "category",
        "required_skills", 
        "image",
        "description",
        "average_salary",
        "future_scope",
        "recommended_courses",
        "roadmap",
    )


# =========================
# Quiz Option Inline
# =========================
class CareerQuizOptionInline(admin.TabularInline):
    model = CareerQuizOption
    extra = 3
    fields = ("option_text", "category", "weight")


# =========================
# Quiz Question Admin
# =========================
@admin.register(CareerQuizQuestion)
class CareerQuizQuestionAdmin(admin.ModelAdmin):
    inlines = [CareerQuizOptionInline]
    list_display = ("question",)
    search_fields = ("question",)


# =========================
# Quiz Result Admin
# =========================
@admin.register(CareerQuizResult)
class CareerQuizResultAdmin(admin.ModelAdmin):
    list_display = ("user", "suggested_career", "total_score", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)
