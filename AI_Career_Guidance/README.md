# 🎓 CareerVidya AI

CareerVidya AI is an intelligent web-based career guidance platform built using Django.  
It helps students discover suitable career paths through Selected Skills ,quiz assessments, resume analysis, and AI chatbot assistance.

🌐 **Live Deployment:** Hosted on Render  
🔗 **Version Controlled:** Git & GitHub  

---

## 🚀 Features

### 👨‍🎓 Student Module
- Secure Registration & Login 
- Student Dashboard
- Account Information
- Select Interest & Multiple Skills
- Career-Based Quiz System
- Instant Score Calculation
- Career Suggestions Based on selected Skills & Quiz Performance
- Resume Upload & Analysis
- Download Career Details as PDF

### 🤖 AI Chatbot
- Integrated AI Chatbot
- Career-related Guidance
- Frontend Chat Interface
- Real-time Response System

### 📄 Resume Analyzer
- Resume Upload
- Skill & Tech Stack Detection
- Career Matching Assistance
- Strengths
- Weakness
- Improvements
- Powered by Groq AI API


### 🛠 Admin Panel
- Custom Admin Dashboard
- Manage Careers, Skills & Categories
- Manage Quiz Questions
- View & Assign Career Suggestions
- Delete Quiz Results
- Analytics Dashboard with Charts

### 🔗 API Integration
- REST API Integration
- External AI Service Integration
- JSON-Based Data Handling
- Secure API Communication

---

## 🏗 Project Architecture

```
AI_Career_Guidance/
│
├── core/                # Main Django Project
│   ├── settings.py
│   ├── urls.py
│
├── accounts/            # Main Website App
├── chatbot/             # AI Chatbot Integration
├── analyzer/            # Resume Analyzer System
│
├── manage.py
└── requirements.txt
```

---

## 🛠 Tech Stack

### 🔹 Frontend
- HTML5
- Tailwind CSS
- JavaScript

### 🔹 Backend
- Python
- Django Framework

### 🔹 AI & APIs
- Groq AI API (Chatbot & Resume Analysis)
- ElevenLabs API (Voice AI Integration)
- Sender API (Email Notifications)

### 🔹 Database
- SQLite (Development)
- PostgreSQL (Production Ready)

### 🔹 Deployment
- Render
- Git
- GitHub

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Anshu1234567899/AI_Career_Guidance
cd AI_Career_Guidance
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate (Windows):

```bash
venv\Scripts\activate
```

Activate (Mac/Linux):

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations

```bash
python manage.py migrate
```

### 5️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 6️⃣ Run Development Server

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## 📊 Core Database Models

- Dashboard
- Users
- StudentProfile  
- Careers
- Skills
- Categories
- CareerQuizQuestion  
- CombinedCareerResult  

---

## 🔒 Security Features

- Staff-Only Admin Access  
- CSRF Protection  
- Role-Based Authentication  
- Secure Form Handling  

---

## 📈 Deployment

This project is deployed on **Render** using:

- GitHub repository integration  
- Automatic builds  
- Production settings configuration  

---

## 🌟 Future Enhancements

- Advanced AI-based Career Prediction  
- Resume Skill Scoring & Ranking System  
- Email Automation Enhancements (Scheduled & Bulk Emails)  
- Advanced Analytics & Reporting Dashboard  
- Multi-language Support  

---

## 👨‍💻 Developed By

**Deepanshu Patyal**  
CareerVidya AI Project  

---

## 📄 License

This project is open-source and available under the MIT License.