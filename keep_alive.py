# flask_app.py

from flask import Flask
from threading import Thread

app = Flask("HopperT")

@app.route('/')
def home():
    return "✅ HopperT đang hoạt động ổn định!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
