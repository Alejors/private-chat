import os
import logging
from pyngrok import ngrok
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


load_dotenv()

connected_clients = {}

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    public_tunnel = None;
    if token:= os.environ.get("NGROK_TOKEN"):
        ngrok.set_auth_token(token)
        public_tunnel = ngrok.connect(8000, bind_tls=True)
        logger.info(f"🚀 Servidor público disponible en: {public_tunnel.public_url.replace('https', 'wss')}/ws")
    else:
        logger.warning("🔒 Servidor levantado localmente en: ws://localhost:8000.")

    yield
    
    # Cuando el servidor se apaga, cerramos las conexiones de clientes
    for client in connected_clients.keys():
        try:
            await client.send_text("⚠️ Servidor cerrándose. Serás desconectado.")
            await client.close()
        except Exception:
            pass

    if public_tunnel:
        ngrok.disconnect(public_tunnel.public_url)
        logger.info("🛑 Túnel de ngrok cerrado.")

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # El primer mensaje que recibimos debería ser el nombre del usuario.
        name = await websocket.receive_text()
        connected_clients[websocket] = name
        while True:
            msg = await websocket.receive_text()
            for client, client_name in connected_clients.items():
                if client != websocket:
                    await client.send_text(f"{name}: {msg}")
    except WebSocketDisconnect as e:
        connected_clients.pop(websocket, None)
        logger.info(f"Cliente {name} desconectado. {e}")
    except Exception as e:
        logger.error(f"Error en la conexión: {e}")
        connected_clients.pop(websocket, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
