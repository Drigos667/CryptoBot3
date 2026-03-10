from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

history = []

system_prompt = """
Você é uma IA especialista em programação e criação de sites.

Se o usuário pedir um site, gere um HTML COMPLETO com:
- <!DOCTYPE html>
- <html>
- <head>
- <body>

O código deve ser funcional e pronto para abrir no navegador.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global history

    data = request.get_json()
    message = data["message"]

    history.append({
        "role": "user",
        "content": message
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":system_prompt}] + history
    )

    reply = response.choices[0].message.content

    history.append({
        "role":"assistant",
        "content":reply
    })

    return jsonify({"reply":reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
