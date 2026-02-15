from django.db import models
from django.contrib.auth.models import User


# =========================
# Skills
# =========================
class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =========================
# Student Profile
# =========================
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, blank=True)
    interest = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


# =========================
# Career Category
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# =========================
# Career Model
# =========================
class Career(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    required_skills = models.ManyToManyField(Skill, blank=True)

    image = models.ImageField(upload_to="career_images/", blank=True, null=True)
    average_salary = models.CharField(max_length=100, blank=True)
    future_scope = models.TextField(blank=True)

    recommended_courses = models.TextField(blank=True)
    roadmap = models.TextField(blank=True)

    def __str__(self):
        return self.name



# =========================
# Quiz Question
# =========================
class CareerQuizQuestion(models.Model):
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


# =========================
# Quiz Option (DYNAMIC VERSION)
# =========================
class CareerQuizOption(models.Model):
    question = models.ForeignKey(CareerQuizQuestion, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    # Instead of ai/web/basic score
    category = models.ForeignKey(
    Category,
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.option_text


# =========================
# Quiz Result
# =========================
class CareerQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    suggested_career = models.ForeignKey(
        Career,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
