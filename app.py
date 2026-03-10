from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
import re

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

history = []

system_prompt = """
Você é um engenheiro de software profissional.

Quando o usuário pedir um site você deve gerar um PROJETO COMPLETO.

O site deve conter:

• Interface moderna
• Layout profissional
• Responsivo
• Navegação entre páginas
• Design bonito
• Animações
• Estrutura real de site

Tecnologias:

HTML5
CSS3
JavaScript

Arquivos obrigatórios:

FILE: index.html
FILE: about.html
FILE: contact.html
FILE: style.css
FILE: script.js

Regras:

1 Não explique nada
2 Não escreva texto fora dos arquivos
3 Gere apenas código
4 Use flexbox ou grid
5 Design moderno

Formato obrigatório:

FILE: index.html
[codigo]

FILE: about.html
[codigo]

FILE: contact.html
[codigo]

FILE: style.css
[codigo]

FILE: script.js
[codigo]
"""

def extract_files(text):

    files = {}

    patterns = {
        "html": r"FILE:\s*index\.html\s*(.*?)FILE:\s*about\.html",
        "about": r"FILE:\s*about\.html\s*(.*?)FILE:\s*contact\.html",
        "contact": r"FILE:\s*contact\.html\s*(.*?)FILE:\s*style\.css",
        "css": r"FILE:\s*style\.css\s*(.*?)FILE:\s*script\.js",
        "js": r"FILE:\s*script\.js\s*(.*)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.S | re.I)
        if match:
            files[key] = match.group(1).strip()

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
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2500,
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
