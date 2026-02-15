from google import genai
client = genai.Client(api_key="AIzaSyB9Gbu5lnOmD3vr9W3TkEqJ5e2RUNTidWo")

models = client.models.list()
for m in models:
    print(m.name)
