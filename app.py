from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
import re

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

history = []

system_prompt = """
Você é um desenvolvedor web profissional.

Sempre que o usuário pedir um site você deve criar uma INTERFACE COMPLETA.

O site deve conter:

- Layout moderno
- Interface visual bonita
- CSS avançado
- Responsivo
- Animações
- Estrutura profissional

Sempre gere os arquivos:

FILE: index.html
FILE: style.css
FILE: script.js

Regras importantes:

1. Não explique nada
2. Não escreva texto fora dos arquivos
3. Gere apenas código
4. O HTML deve linkar os arquivos CSS e JS
5. Use design moderno

Formato obrigatório da resposta:

FILE: index.html
[codigo]

FILE: style.css
[codigo]

FILE: script.js
[codigo]
"""


def extract_files(text):

    files = {}

    html_match = re.search(r"FILE:\s*index\.html\s*(.*?)FILE:\s*style\.css", text, re.S | re.I)
    css_match = re.search(r"FILE:\s*style\.css\s*(.*?)FILE:\s*script\.js", text, re.S | re.I)
    js_match = re.search(r"FILE:\s*script\.js\s*(.*)", text, re.S | re.I)

    if html_match:
        files["html"] = html_match.group(1).strip()

    if css_match:
        files["css"] = css_match.group(1).strip()

    if js_match:
        files["js"] = js_match.group(1).strip()

    return files


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    global history

    data = request.get_json()
    message = data.get("message", "")

    history.append({
        "role": "user",
        "content": message
    })

    history = history[-6:]

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1500,
            messages=[{"role": "system", "content": system_prompt}] + history
        )

        reply = response.choices[0].message.content

        history.append({
            "role": "assistant",
            "content": reply
        })

        files = extract_files(reply)

        return jsonify({
            "reply": reply,
            "files": files
        })

    except Exception as e:

        return jsonify({
            "reply": "Erro ao gerar resposta da IA",
            "error": str(e)
        })


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
