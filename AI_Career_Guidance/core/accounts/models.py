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
    EDUCATION_CHOICES = [
        ('10th', '10th'),
        ('12th', '12th'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Post Graduate'),
    ]

    STREAM_CHOICES = [
        ('arts', 'Arts'),
        ('commerce', 'Commerce'),
        ('medical', 'Medical'),
        ('non-medical', 'Non Medical'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, blank=True)
    graduation_field = models.CharField(max_length=100, blank=True)
    post_graduation_field = models.CharField(max_length=100, blank=True)
    location_preference = models.CharField(max_length=100, blank=True)
    interest = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    personality_quiz_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# =========================
# Student Skill with Proficiency
# =========================
class StudentSkill(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="student_skills"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)  # 1–10 scale

    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name} ({self.level})"


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
    DIFFICULTY_LEVEL = [
        (1, "Very Easy"),
        (2, "Easy"),
        (3, "Moderate"),
        (4, "Hard"),
        (5, "Very Hard"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True)
    image = models.ImageField(upload_to="career_images/", blank=True, null=True)
    average_salary = models.CharField(max_length=100, blank=True)
    future_scope = models.TextField(blank=True)
    recommended_courses = models.TextField(blank=True)
    roadmap = models.TextField(blank=True)
    difficulty_level = models.IntegerField(choices=DIFFICULTY_LEVEL, default=3)
    demand_score = models.IntegerField(default=5)  # 1–10 scale
    min_education = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


# =========================
# Career Quiz Question
# =========================
class CareerQuizQuestion(models.Model):
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


# =========================
# Career Quiz Option
# =========================
class CareerQuizOption(models.Model):
    question = models.ForeignKey(
        CareerQuizQuestion,
        on_delete=models.CASCADE,
        related_name="options"  # <-- important for prefetch_related
    )
    option_text = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.option_text


# =========================
# Combined Career Result
# =========================
class CombinedCareerResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    suggested_career = models.ForeignKey(Career, on_delete=models.SET_NULL, null=True, blank=True)
    skill_score = models.IntegerField(default=0)
    quiz_score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    match_percentage = models.PositiveIntegerField(null=True, blank=True)
    skill_gap = models.JSONField(null=True, blank=True)  # 

    def __str__(self):
        return f"{self.student.user.username} - {self.suggested_career} ({self.total_score})"

    @classmethod
    def latest_for_student(cls, student):
        return cls.objects.filter(student=student).order_by("-created_at").first()


# =========================
# Career Quiz Result
# =========================
class CareerQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)  # store quiz answers in JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Quiz Result"