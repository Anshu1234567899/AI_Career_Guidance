from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from groq import Groq
import json
import requests
import base64

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

    user_lower = user_message.lower()

    # ✅ Identity Shortcut
    identity_keywords = [
        "who are you",
        "tum kaun ho",
        "ap kaun ho",
        "tell me about yourself",
        "your name"
    ]

    if any(keyword in user_lower for keyword in identity_keywords):
        return JsonResponse({
            "reply": "I'm your CareerVidya AI Career Mentor 😊",
            "audio": None
        })

    # 🔹 Length Rule
    word_count = len(user_message.split())
    length_rule = "Reply in 1–2 short lines only." if word_count <= 5 else "Reply in max 3–4 short lines."

    user_name = request.user.first_name or "Student"

    system_prompt = f"""
You are a smart female AI Career Mentor chatting like WhatsApp.

User name: {user_name}

Rules:
- Always speak in feminine Hinglish tone (deti hun, samajhti hun, karungi).
- Never use masculine tone.
- Keep replies short.
- Ask max ONE follow-up question.
- Never write more than 4 short lines.
- {length_rule}
"""

    try:

        # 🔹 Session Memory Limited
        if "chat_history" not in request.session:
            request.session["chat_history"] = []

        chat_history = request.session["chat_history"]
        limited_history = chat_history[-8:]

        messages = [{"role": "system", "content": system_prompt}]
        messages += limited_history
        messages.append({"role": "user", "content": user_message})

        # 🔹 GROQ CALL
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=80,
        )

        reply = completion.choices[0].message.content.strip()
        reply = "\n".join(reply.split("\n")[:4])

        # 🔹 Save Memory
        request.session["chat_history"].append({"role": "user", "content": user_message})
        request.session["chat_history"].append({"role": "assistant", "content": reply})
        request.session.modified = True

        # =====================
        # 🔊 ELEVENLABS TTS
        # =====================

        audio_base64 = None

        try:
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            headers = {
                "xi-api-key": settings.ELEVEN_API_KEY,
                "Content-Type": "application/json"
            }

            short_reply_for_voice = reply[:300]  # smaller = faster

            payload = {
                "text": short_reply_for_voice,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.7,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }

            tts_response = requests.post(
                tts_url,
                json=payload,
                headers=headers,
                timeout=6
            )

            if tts_response.ok:
                audio_base64 = base64.b64encode(
                    tts_response.content
                ).decode("utf-8")

        except Exception as e:
            print("TTS ERROR:", e)

        return JsonResponse({
            "reply": reply,
            "audio": audio_base64
        })

    except Exception as e:
        print("❌ GROQ ERROR:", e)
        return JsonResponse({"reply": "AI backend error"}, status=500)