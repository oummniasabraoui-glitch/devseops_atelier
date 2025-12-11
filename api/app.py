from flask import Flask, request
import sqlite3
import subprocess
import hashlib
import os
import re

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "not-for-production")


############################################
# 1. LOGIN – SQL Injection corrigée
############################################
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username=? AND password=?"
    cursor.execute(query, (username, password))

    result = cursor.fetchone()
    if result:
        return {"status": "success", "user": username}
    return {"status": "error", "message": "Invalid credentials"}


############################################
# 2. PING – Command Injection empêchée
############################################
@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")

    # Validation stricte
    if not re.match(r"^[a-zA-Z0-9\.\-]+$", host):
        return {"error": "Invalid host"}, 400

    cmd = ["ping", "-c", "1", host]

    try:
        output = subprocess.check_output(cmd)  # pas de shell=True
        return {"output": output.decode()}
    except Exception:
        return {"error": "Ping failed"}, 400


############################################
# 3. COMPUTE – Suppression de eval()
############################################
@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "1+1")

    # Expression autorisée : chiffres + opérateurs simples
    if not re.match(r"^[0-9+\-*/(). ]+$", expression):
        return {"error": "Invalid expression"}, 400

    try:
        result = eval(expression, {"__builtins__": None}, {})
        return {"result": result}
    except Exception:
        return {"error": "Computation error"}, 400


############################################
# 4. HASH – Remplacement de MD5
############################################
@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "admin")
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    return {"sha256": hashed}


############################################
# 5. READFILE – Protection Directory Traversal
############################################
@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "test.txt")

    # Accès limité à un répertoire précis
    base_dir = os.path.abspath("files")
    file_path = os.path.abspath(os.path.join(base_dir, filename))

    if not file_path.startswith(base_dir):
        return {"error": "Unauthorized file access"}, 403

    try:
        with open(file_path, "r") as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"error": "File not found"}, 404


############################################
# 6. DEBUG – Retrait des infos sensibles
############################################
@app.route("/debug", methods=["GET"])
def debug():
    return {"debug": "disabled"}


############################################
# 7. HELLO – inchangé
############################################
@app.route("/hello", methods=["GET"])
def hello():
    return {"message": "Welcome to the secure DevSecOps API"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
