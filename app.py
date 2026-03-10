from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
import re

app = Flask(__name__)

# conectar API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# histórico curto
history = []

system_prompt = """
Você é uma IA especialista em desenvolvimento web.

Quando o usuário pedir um site você deve gerar um projeto completo com:

FILE: index.html
FILE: style.css
FILE: script.js

Use HTML5, CSS3 e JavaScript moderno.

Formato da resposta:

FILE: index.html
[codigo html]

FILE: style.css
[codigo css]

FILE: script.js
[codigo javascript]
"""

def extract_files(text):

    files = {}

    html = re.search(r"FILE: index.html(.*?)FILE: style.css", text, re.S)
    css = re.search(r"FILE: style.css(.*?)FILE: script.js", text, re.S)
    js = re.search(r"FILE: script.js(.*)", text, re.S)

    if html:
        files["html"] = html.group(1).strip()

    if css:
        files["css"] = css.group(1).strip()

    if js:
        files["js"] = js.group(1).strip()

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

    # limitar histórico
    history = history[-6:]

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1200,
            temperature=0.2,
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
