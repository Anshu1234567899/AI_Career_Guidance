from django.contrib import admin
from .models import (
    Skill,
    StudentProfile,
    StudentSkill,
    Career,
    CareerQuizQuestion,
    CareerQuizOption,
    CareerQuizResult,
    Category
)


# =========================
# Skill Admin
# =========================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# =========================
# StudentSkill Inline
# =========================
class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 1
    fields = ("skill", "level")


# =========================
# StudentProfile Admin
# =========================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "interest",
        "profile_picture",
    )
    search_fields = (
        "user__username",
        "user__email",
        "interest",
    )
    inlines = [StudentSkillInline]


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
    filter_horizontal = ("required_skills",)

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
    extra = 2
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
    # Sirf existing model fields + admin methods
    list_display = ('user', 'get_quiz_date', 'suggested_career', 'total_score')
    search_fields = ('user__username', 'user__email')

    # agar model me quiz_date nahi hai, hum admin me define kar rahe hain
    def get_quiz_date(self, obj):
        # agar model me created_at ya timestamp field hai to use karo
        return getattr(obj, 'created_at', "N/A")
    get_quiz_date.short_description = "Quiz Date"

    def suggested_career(self, obj):
        return obj.top_career.name if getattr(obj, 'top_career', None) else "N/A"
    suggested_career.short_description = "Suggested Career"

    def total_score(self, obj):
        return getattr(obj, 'score', "N/A")
    total_score.short_description = "Total Score"