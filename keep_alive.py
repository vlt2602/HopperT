# keep_alive.py

from quart import Quart
from threading import Thread

app = Quart("HopperT")

@app.route('/')
async def home():
    return "✅ HopperT đang hoạt động ổn định!"

def run():
    import asyncio
    asyncio.run(app.run_task(host='0.0.0.0', port=8080))

def keep_alive():
    t = Thread(target=run)
    t.start()
