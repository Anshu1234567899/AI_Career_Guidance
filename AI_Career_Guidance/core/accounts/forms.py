from django import forms
from .models import Career, Skill, Category, StudentProfile, CareerQuizQuestion, CareerQuizOption
from django.contrib.auth.models import User

# =========================
# User Update Form
# =========================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name', 'email', 'is_active', 'is_staff']


# =========================
# Career Admin Form
# =========================
class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = [
            'name',
            'description',
            'required_skills',
            'image',
            'average_salary',
            'future_scope',
            'recommended_courses',
            'roadmap',
            'category',
        ]
        widgets = {
            'required_skills': forms.SelectMultiple(attrs={
                'size': '8',
                'style':'width:100%; padding:6px; border-radius:5px; background:#1c1c1c; color:#fff; border:1px solid #555;',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'style':'width:100%; padding:6px; border-radius:5px; background:#1c1c1c; color:#fff; border:1px solid #555;',
            }),
        }


# =========================
# Skill Admin Form
# =========================
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-400'
            }),
        }


# =========================
# Contact Form
# =========================
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Your Name', 'class': 'form-input'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email', 'class': 'form-input'
    }))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Subject', 'class': 'form-input'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Your Message', 'class': 'form-input'
    }))


# =========================
# Category Admin Form
# =========================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full', 'rows': 3}),
        }


# =========================
# Combined Student Career Form
# =========================
LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('expert', 'Expert'),
]

class CombinedCareerForm(forms.Form):
    # --- Skills Multi-select ---
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
        required=False,
        label="Select Your Skills"
    )

    # --- Location Preference ---
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your preferred location'
        }),
        label="Location Preference"
    )

    # --- Dynamic Quiz Questions ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = CareerQuizQuestion.objects.all()
        for question in questions:
            options = question.options.all()
            choices = [(opt.id, opt.option_text) for opt in options]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.question,
                required=True
            )