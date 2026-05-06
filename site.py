import json
import os

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_FILE = "data/artigos_ceara.json"


@app.route("/artigos")
def get_opovo():
    if not os.path.exists(DATA_FILE):
        return jsonify({"error": "Dados não disponíveis ainda", "artigos": []}), 503

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Erro ao ler dados", "artigos": []}), 500


@app.route("/")
def index():
    return jsonify({"Status": "rodando", "endpoints": ["/artigos"]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
