from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

history = []

system_prompt = """
Você é uma IA engenheira de software de nível mundial.

Especialista em:
- Python
- JavaScript
- HTML
- CSS
- C
- C++
- Java
- APIs
- Machine Learning
- Inteligência Artificial
- Banco de Dados
- Segurança
- Automação
- Web Apps
- Bots
- Games
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

    if len(history) > 20:
        history.pop(0)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + history
    )

    reply = response.choices[0].message.content

    history.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
