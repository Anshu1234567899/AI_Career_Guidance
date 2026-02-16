from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from .models import Skill, StudentProfile
from django.shortcuts import get_object_or_404
from .models import Career
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserUpdateForm, CareerForm ,ContactForm
from django.conf import settings
from .forms import SkillForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from .models import CareerQuizQuestion, CareerQuizOption, CareerQuizResult ,Category
from django.http import HttpResponse
import subprocess

@never_cache
@login_required
def dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    career_scores = recommend_career(profile)
    top_career = career_scores[0][0] if career_scores and career_scores[0][0] else None

    completion = 0

    # 1️⃣ Profile picture
    if profile.profile_picture:
        completion += 25

    # 2️⃣ Interest
    if profile.interest:
        completion += 25

    # 3️⃣ Skills (at least 1)
    if profile.skills.exists():
        completion += 25

    # 4️⃣ Career matched
    if top_career:
        completion += 25

    return render(request, "accounts/dashboard.html", {
        "profile": profile,
        "career": top_career,
        "all_careers": career_scores,
        "completion": completion
    })


def home(request):
    return render(request, 'accounts/home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            return render(request, 'accounts/register.html', {
                'error': 'All fields are required'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        return redirect('login')

    return render(request, 'accounts/register.html')

@login_required
def edit_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    skills = Skill.objects.all()

    if request.method == "POST":
        profile.interest = request.POST.get("interest", "")

        # Always update skills, even if none selected
        selected_skills = request.POST.getlist("skills")
        profile.skills.set(selected_skills)

        # Profile picture update
        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()
        return redirect("dashboard")

    return render(request, "accounts/edit_profile.html", {
        "profile": profile,
        "skills": skills
    })



def recommend_career(profile):
    skill_names = [skill.name.lower() for skill in profile.skills.all()]
    interest = profile.interest.lower() if profile.interest else ""

    career_scores = []

    # Rule-based scoring
    if "python" in skill_names or "machine learning" in skill_names:
        career = Career.objects.filter(name__iexact="Data Scientist").first()
        if career: career_scores.append((career, 80))  # 80% match

    if "javascript" in skill_names or "html" in skill_names:
        career = Career.objects.filter(name__iexact="Web Developer").first()
        if career: career_scores.append((career, 70))

    if "ai" in skill_names:
        career = Career.objects.filter(name__iexact="AI/ML Engineer").first()
        if career: career_scores.append((career, 85))

    if "python" in skill_names:
        career = Career.objects.filter(name__iexact="Software Developer").first()
        if career: career_scores.append((career, 75))

    if not career_scores:
        return [(None, 0)]

    # Sort by highest score
    career_scores.sort(key=lambda x: x[1], reverse=True)
    return career_scores



@login_required
def career_detail(request, career_id):
    career = get_object_or_404(Career, id=career_id)

    # Split comma-separated fields into lists
    courses = career.recommended_courses.split(',') if career.recommended_courses else []
    roadmap_steps = career.roadmap.split(',') if career.roadmap else []

    return render(request, 'accounts/career_detail.html', {
        'career': career,
        'courses': courses,
        'roadmap_steps': roadmap_steps,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def is_admin(user):
    return user.is_authenticated and user.is_staff

# 🧠 Admin Dashboard
@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_careers = Career.objects.count()
    total_skills = Skill.objects.count()
    total_quiz_questions = CareerQuizQuestion.objects.count()

    context = {
        'total_users': total_users,
        'total_careers': total_careers,
        'total_skills': total_skills,
        "total_quiz_questions": total_quiz_questions,
    }

    # ✅ Template path correct
    return render(request, 'accounts/admin/dashboard.html', context)








@staff_member_required
def admin_users(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    users = User.objects.all().order_by('-id')  # 👈 latest first

    # 🔍 Search (username + email)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    # 🎯 Status filter
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    # 📄 Pagination
    paginator = Paginator(users, 5)  # 👈 5 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'users': users,
        'search': search,
        'status': status
    }

    return render(request, 'accounts/admin/users.html', context)


@staff_member_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserUpdateForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_users')

    return render(request, 'accounts/admin/user_edit.html', {'form': form})


@staff_member_required
@require_POST  # ensures only POST method is allowed
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully 🗑️")
    return redirect('admin_users')

@staff_member_required
def admin_user_add(request):
    form = UserUpdateForm(request.POST or None)  # ya UserCreationForm agar new user
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_users')

    return render(request, 'accounts/admin/user_edit.html', {'form': form})


@staff_member_required
@require_POST
def admin_users_bulk_delete(request):
    user_ids = request.POST.getlist('user_ids')  # checkbox ids
    if user_ids:
        User.objects.filter(id__in=user_ids).delete()
    messages.success(request, "Selected users deleted successfully 🗑️")
    return redirect('admin_users')
# ================= CAREERS =================
@staff_member_required
def admin_careers(request):
    search = request.GET.get('search', '')
    careers = Career.objects.all().order_by('-id')  # latest first

    # 🔍 Search by name / description
    if search:
        careers = careers.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    # 📄 Pagination
    paginator = Paginator(careers, 5)  # 5 careers per page
    page_number = request.GET.get('page')
    careers = paginator.get_page(page_number)

    return render(request, 'accounts/admin/careers.html', {
        'careers': careers,
        'search': search
    })

@staff_member_required
@staff_member_required
def admin_career_add(request):
    form = CareerForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Career added successfully ✅")
        return redirect('admin_careers')

    return render(request, 'accounts/admin/career_form.html', {
        'form': form
    })


@staff_member_required
def admin_career_edit(request, career_id):
    career = get_object_or_404(Career, id=career_id)
    form = CareerForm(request.POST or None, request.FILES or None, instance=career)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Career updated successfully ✨")
        return redirect('admin_careers')

    return render(request, 'accounts/admin/career_form.html', {
        'form': form
    })
   

@staff_member_required
def admin_career_delete(request, career_id):
    career = get_object_or_404(Career, id=career_id)
    career.delete()
    return redirect('admin_careers')


@staff_member_required
def admin_skills(request):
    search = request.GET.get('search', '')
    skills = Skill.objects.all().order_by('-id')  # latest first

    # 🔍 Search by name
    if search:
        skills = skills.filter(name__icontains=search)

    # Pagination
    paginator = Paginator(skills, 5)  # 5 skills per page
    page_number = request.GET.get('page')
    skills = paginator.get_page(page_number)

    return render(request, 'accounts/admin/skills.html', {
        'skills': skills,
        'search': search
    })


@staff_member_required
@require_POST
def admin_skills_bulk_delete(request):
    skill_ids = request.POST.getlist('skill_ids')
    if skill_ids:
        Skill.objects.filter(id__in=skill_ids).delete()
        messages.success(request, "Selected skills deleted successfully 🧠")
    return redirect('admin_skills')


@staff_member_required
def admin_skill_add(request):
    form = SkillForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Skill added successfully 🧠")

        return redirect('admin_skills')
    return render(request, 'accounts/admin/skill_form.html', {'form': form})

@staff_member_required
def admin_skill_edit(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_skills')
    return render(request, 'accounts/admin/skill_form.html', {'form': form})

@staff_member_required
def admin_skill_delete(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.delete()
    return redirect('admin_skills')


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            full_message = f"Message from {name} ({email}):\n\n{message}"

            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,       # From email
                ['patyaldeepanshu05@gmail.com'],     # Apna email jahan receive karna hai
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent! ✅")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'accounts/contact.html', {'form': form})

@login_required
def career_quiz(request):
    questions = CareerQuizQuestion.objects.prefetch_related('careerquizoption_set')

    if request.method == "POST":
        scores = {}

        for question in questions:
            selected_option_id = request.POST.get(f"question_{question.id}")

            if selected_option_id:
                try:
                    option = CareerQuizOption.objects.get(id=selected_option_id)

                    if option.category:  # safety check
                        scores[option.category] = scores.get(option.category, 0) + option.weight

                except CareerQuizOption.DoesNotExist:
                    pass

        if not scores:
            return render(request, "accounts/result.html", {
                "career": "No Result",
                "description": "Please answer all questions."
            })

        best_category = max(scores, key=scores.get)
        final_score = scores[best_category]

        career_obj = Career.objects.filter(category=best_category).first()

        if career_obj:
            career_name = career_obj.name
            description = career_obj.description
        else:
            career_name = best_category.name if best_category else "No Category Found"
            description = "This category matches your personality."

        CareerQuizResult.objects.create(
            user=request.user,
            suggested_career=career_obj,
            total_score=final_score
        )

        return render(request, "accounts/result.html", {
            "career": career_name,
            "description": description,
            "final_score": final_score,
            "category": best_category.name if best_category else "",
            "scores": scores
        })

    return render(request, "accounts/quiz.html", {"questions": questions})



@login_required
def admin_quiz_list(request):
    questions = CareerQuizQuestion.objects.all()
    return render(request, "accounts/admin/quiz_list.html", {"questions": questions})

@login_required
def admin_quiz_add(request):
    categories = Category.objects.all()

    if request.method == "POST":
        question_text = request.POST.get("question")
        if not question_text:
            return render(request, "accounts/admin/quiz_add.html", {
                "categories": categories,
                "error": "Question is required."
            })

        question = CareerQuizQuestion.objects.create(question=question_text)

        for i in range(1, 4):  # assuming 3 options per question
            opt_text = request.POST.get(f"option{i}_text")
            category_id = request.POST.get(f"option{i}_category")
            weight = request.POST.get(f"option{i}_weight")

            if opt_text and category_id:
                CareerQuizOption.objects.create(
                    question=question,
                    option_text=opt_text,
                    category_id=category_id,
                    weight=int(weight or 1)
                )

        return redirect('admin_quiz_list')

    return render(request, "accounts/admin/quiz_add.html", {"categories": categories})

@login_required
def admin_quiz_edit(request, id):
    question = get_object_or_404(CareerQuizQuestion, id=id)
    options = question.careerquizoption_set.all()
    categories = Category.objects.all()

    if request.method == "POST":
        question.question = request.POST.get("question")
        question.save()

        for i, opt in enumerate(options, start=1):
            opt.option_text = request.POST.get(f"option{i}_text")
            opt.category_id = request.POST.get(f"option{i}_category")
            opt.weight = int(request.POST.get(f"option{i}_weight") or 1)
            opt.save()

        return redirect('admin_quiz_list')

    return render(request, "accounts/admin/quiz_edit.html", {
        "question": question,
        "options": options,
        "categories": categories
    })

@login_required
def admin_quiz_delete(request, id):
    question = get_object_or_404(CareerQuizQuestion, id=id)
    question.delete()
    return redirect('admin_quiz_list')


from django.db.models import Q

@login_required
def skill_based_careers(request):
    profile = StudentProfile.objects.get(user=request.user)

    user_skills = profile.skills.all()
    careers = Career.objects.none()

    # 1️⃣ Skill match
    if user_skills.exists():
        careers = Career.objects.filter(
            required_skills__in=user_skills
        )

    # 2️⃣ Interest match
    if profile.interest:
        interest_based = Career.objects.filter(
            category__name__icontains=profile.interest
        )
        careers = careers | interest_based

    careers = careers.distinct()

    return render(request, 'accounts/skill_based.html', {
        'careers': careers
    })

def run_migrations(request):
    # TEMPORARY: Bypass superuser check for deployment migration

    # Directly run migrate without checking user
    result = subprocess.run(
        ["python", "manage.py", "migrate", "--noinput"],
        capture_output=True, text=True
    )
    return HttpResponse(f"<pre>{result.stdout}\n{result.stderr}</pre>")
