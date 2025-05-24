from quart import Quart

app = Quart(__name__)

@app.route('/')
async def home():
    return "✅ HopperT is running!"

@app.route('/healthcheck')
async def healthcheck():
    return "✅ HopperT is alive and healthy!"
