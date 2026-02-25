from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from groq import Groq
import json

client = Groq(api_key=settings.GROQ_API_KEY)

@login_required
@csrf_exempt
def career_chatbot(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"reply": "Invalid JSON"}, status=400)

    user_message = data.get("message", "").strip()
    if not user_message:
        return JsonResponse({"reply": "Message cannot be empty"}, status=400)

    # 🔹 SHORT / LONG QUESTION DETECTION
    word_count = len(user_message.split())
    if word_count <= 5:
        length_rule = "Reply in 1–2 short lines only."
    else:
        length_rule = "Reply in max 3–4 short lines."

    # 🔹 PERSONALIZED SYSTEM PROMPT
    user_name = request.user.first_name or "Student"  # fallback if first_name empty
    system_prompt = f"""
You are a highly intelligent AI Career Mentor, just like ChatGPT, chatting with a student on WhatsApp.

User name: {user_name}

Rules:
- Read the user's message carefully and reply based on exactly what they said.
- Always use the user's name naturally in replies. Example: "Hello {user_name}, kaise ho?"
- Be casual, friendly, motivating in Hinglish.
- Give actionable advice if relevant.
- Suggest skills, courses, or next steps if possible.
- Ask at most ONE follow-up question.
- Keep answers short (1–2 lines if question is short, 3–4 lines if long).
- Never say you are AI or repeat your introduction.
- Avoid generic responses; reply dynamically to the user's message.
- {length_rule}
"""

    try:
        # 🔹 MULTI-TURN MEMORY (using Django session)
        if "chat_history" not in request.session:
            request.session["chat_history"] = []

        # Build messages list for API
        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.session["chat_history"]:
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # 🔹 CALL GROQ API
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.8,    # creative and human-like
            max_tokens=300,     # enough for detailed short advice
        )

        reply = completion.choices[0].message.content.strip()

        # Save conversation in session
        request.session["chat_history"].append({"role": "user", "content": user_message})
        request.session["chat_history"].append({"role": "assistant", "content": reply})
        request.session.modified = True  # ensure session saves

        return JsonResponse({"reply": reply})

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        return JsonResponse({"reply": "AI backend error"}, status=500)