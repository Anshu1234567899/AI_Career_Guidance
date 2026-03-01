from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from groq import Groq
import json
import requests
import base64
import re

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
    user_name = request.user.first_name or request.user.username or "Student"

    # =====================================================
    # SIMPLE GREETING (NO MODEL CALL)
    # =====================================================

    simple_greetings = ["hi", "hello", "hey"]

    if user_lower in simple_greetings:
        request.session["chat_history"] = []
        request.session["chat_language"] = "english"

        reply = f"Hello {user_name}, how can I help you with your career today?"

        return JsonResponse({
            "reply": reply,
            "audio": None
        })

    # =====================================================
    # LANGUAGE CONTROL SYSTEM
    # =====================================================

    if "chat_language" not in request.session:
        request.session["chat_language"] = "english"

    hindi_triggers = [
        "hindi me baat karo",
        "talk in hindi",
        "speak in hindi",
        "hindi mein baat karo"
    ]

    english_triggers = [
        "talk in english",
        "english me baat karo",
        "speak in english"
    ]

    # Switch to Hindi
    if any(trigger in user_lower for trigger in hindi_triggers):
        request.session.flush()
        request.session["chat_language"] = "hindi"

    # Switch to English
    if any(trigger in user_lower for trigger in english_triggers):
        request.session.flush()
        request.session["chat_language"] = "english"

    current_language = request.session.get("chat_language", "english")

    # =====================================================
    # LANGUAGE INSTRUCTION
    # =====================================================

    if current_language == "hindi":
        language_instruction = """
Reply ONLY in pure Hindi using Devanagari script.
Do NOT use English words.
"""
    else:
        language_instruction = """
Reply STRICTLY in English only.
Never use Hindi words.
Never mix languages.
"""

    # =====================================================
    # IDENTITY CHECK
    # =====================================================

    identity_keywords = [
        "who are you",
        "tell me about yourself",
        "your name"
    ]

    if any(keyword in user_lower for keyword in identity_keywords):
        reply = f"Hello {user_name}, I'm your AI Career Mentor. I'm here to guide you with smart career advice."
        return JsonResponse({
            "reply": reply,
            "audio": None
        })

    # =====================================================
    # RESPONSE LENGTH CONTROL
    # =====================================================

    word_count = len(user_message.split())
    length_rule = "Reply in 1–2 short lines only." if word_count <= 5 else "Reply in max 3–4 short lines."

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    system_prompt = f"""
You are a smart female AI Career Mentor chatting casually like chatgpt, WhatsApp.

User name: {user_name}

Rules:
- ALWAYS start reply with: "{user_name},"
- Speak in feminine tone.
- Keep answers short.
- Ask maximum ONE follow-up question.
- Never exceed 4 short lines.
- {language_instruction}
- {length_rule}
"""

    try:

        # =====================================================
        # SESSION MEMORY
        # =====================================================

        if "chat_history" not in request.session:
            request.session["chat_history"] = []

        chat_history = request.session["chat_history"]
        limited_history = chat_history[-6:]

        messages = [{"role": "system", "content": system_prompt}]
        messages += limited_history
        messages.append({"role": "user", "content": user_message})

        # =====================================================
        # GROQ API CALL
        # =====================================================

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.6,
            max_tokens=120,
        )

        reply = completion.choices[0].message.content.strip()
        reply = "\n".join(reply.split("\n")[:4])

        # =====================================================
        # HARD ENGLISH SAFETY (UNICODE ONLY)
        # =====================================================

        if current_language == "english":
            # Remove any Hindi Unicode characters
            reply = re.sub(r'[\u0900-\u097F]+', '', reply)

        # Ensure greeting exists
        if not reply.lower().startswith(f"{user_name.lower()}"):
            reply = f"Hello {user_name}, {reply}"

        # Save memory
        request.session["chat_history"].append(
            {"role": "user", "content": user_message}
        )
        request.session["chat_history"].append(
            {"role": "assistant", "content": reply}
        )
        request.session.modified = True

        # =====================================================
        # ELEVENLABS TTS
        # =====================================================

        audio_base64 = None

        try:
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            headers = {
                "xi-api-key": settings.ELEVEN_API_KEY,
                "Content-Type": "application/json"
            }

            payload = {
                "text": reply[:300],
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
        print("GROQ ERROR:", e)
        return JsonResponse({"reply": "AI backend error"}, status=500)