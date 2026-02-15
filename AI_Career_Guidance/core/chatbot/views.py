from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from google import genai
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

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

    # 🔹 LIGHTWEIGHT PROMPT (FAST + HUMAN)
    prompt = f"""
You are an AI Career Mentor.
Talk like a real human chatting on WhatsApp.
{length_rule}
No long explanations. No essays.
Ask at most ONE follow-up question.

User question:
{user_message}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )

        reply = response.text.strip()

        # 🔹 HARD LIMIT (safety net)
        if len(reply) > 400:
            reply = reply[:400] + "..."

        return JsonResponse({"reply": reply})

    except Exception as e:
        print("❌ GEMINI ERROR:", e)
        return JsonResponse({"reply": "AI backend error"}, status=500)
