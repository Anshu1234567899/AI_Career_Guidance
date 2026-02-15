from django import forms
from .models import Career
from django.contrib.auth.models import User
from .models import Skill


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff']


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
        ]
        

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']  # Add more fields if Skill model me hai
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-400'}),
        }


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