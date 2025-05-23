from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return "✅ HopperX đang chạy!"


@app.route('/healthcheck')
def healthcheck():
    return "✅ HopperX vẫn sống!"
