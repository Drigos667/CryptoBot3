from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)

# API KEY
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# memória da conversa
history = []

# prompt da IA
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

REGRAS:

1 Sempre gere código COMPLETO e funcional.
2 Explique o código de forma simples.
3 Use boas práticas de programação.
4 Se o projeto for grande, divida em etapas.
5 Use bibliotecas modernas.
6 O código deve estar pronto para rodar.

Formato da resposta:

EXPLICAÇÃO:
Explicação simples

CÓDIGO:
```python
# código aqui

DICAS:
Boas práticas ou melhorias
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

# limite de memória
if len(history) > 20:
    history.pop(0)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "system", "content": system_prompt}] + history,
    temperature=0.2,
    max_tokens=4096
)

reply = response.choices[0].message.content

history.append({
    "role": "assistant",
    "content": reply
})

return jsonify({"reply": reply})

if name == "main":
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
