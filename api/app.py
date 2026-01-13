import hashlib
import subprocess
from flask import Flask, request

from utils import load_user

app = Flask(__name__)

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return result

ADMIN_PASSWORD = "123456"

@app.route("/hello")
def hello():
    name = request.args.get("name", "user")
    return f"<h1>Hello {name}</h1>"

@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    stored_password = load_user(username)

    if stored_password == password:
        return "Logged in"
    return "Invalid credentials"

if __name__ == "__main__":
    app.run(debug=True)
