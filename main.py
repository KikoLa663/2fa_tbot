import logging
from contextlib import asynccontextmanager

from telegram import Update
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bot_handlers import bot, configure_bot, route_update

logging.getLogger().setLevel(logging.INFO)

PORT = 8080

@asynccontextmanager
async def lifespan(app: FastAPI):
    from pyngrok import ngrok

    http_tunnel = ngrok.connect(PORT, bind_tls=True)
    public_url = http_tunnel.public_url
    webhook_url = f"{public_url}/webhook"
    await configure_bot(webhook_url)

    yield

app = FastAPI(
    description="Telegram bot",
    version="0.0.1",
    lifespan=lifespan
)

@app.post("/webhook")
async def respond(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await route_update(update)
    except Exception as e:
        logging.error(f"Webhook update error: {e}", exc_info=True)
    return JSONResponse(
        content={
            "status": "ok"
        }
    )
