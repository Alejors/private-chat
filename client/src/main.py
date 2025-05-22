import re
import logging
import asyncio
import aioconsole
import websockets


MAX_RETRIES=3
QUIT_STRINGS=["--exit", "--salir", "--quit", "--q"]
HELP_STRINGS=["--ayuda", "--help", "--h"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

async def send(ws):
    try:
        while True:
            msg = await aioconsole.ainput()
            if msg.strip().lower() in QUIT_STRINGS:
                logger.info("🛑 Cliente cerrado por el usuario.")
                await ws.close()
                return True
            if msg.strip().lower() in HELP_STRINGS:
                logger.info("Para salir del cliente puedes escribir --exit, --salir, --quit o --q")
            if msg.strip():
                await ws.send(msg)
    except websockets.exceptions.ConnectionClosed:
        logger.error("La conexión se cerró, no se puede enviar mensajes.")
    except asyncio.CancelledError:
        pass
    return False


async def receive(ws):
    try:
        async for msg in ws:
            logger.info(msg)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Conexión cerrada desde el servidor.")
    except asyncio.CancelledError:
        pass
    return False


def get_server_url() -> str:
    regex = r'^wss?://([a-zA-Z0-9.-]+)(:\d+)?(/[\w\-./?%&=]*)?$'
    for attempt in range(MAX_RETRIES):
        url = input("Ingresa la URL del servidor (ej: wss://...): ")
        if re.match(regex, url):
            return url
        logger.warning(f"URL inválida. Intento {attempt + 1} de {MAX_RETRIES}.")
    raise ValueError("URL inválida. Intentos máximos superados.")

async def main():
    url = get_server_url()
    name = input("Ingresa tu nombre: ").strip()
    
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            async with websockets.connect(url) as ws:
                retries = 0
                # Enviar el nombre primero al servidor
                await ws.send(name)
                logger.info(f"Conectado a {url}. Puedes empezar a chatear.")
                
                send_task = asyncio.create_task(send(ws))
                receive_task = asyncio.create_task(receive(ws))
                done, pending = await asyncio.wait(
                    [send_task, receive_task], 
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
                    
                results = await asyncio.gather(*done)
                if any(results):
                    break
                
                await asyncio.gather(*pending, return_exceptions=True)

        except (ConnectionRefusedError, OSError):
            retries += 1
            logger.warning("No se pudo conectar. Reintentando en 3 segundos...")
            await asyncio.sleep(3)

        except KeyboardInterrupt:
            logger.info("🛑 Cliente cerrado por el usuario.")
            
        except websockets.exceptions.ConnectionClosedOK:
            logger.warning("Conexión cerrada por el servidor.")
            break
        
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            break
    else:
        logger.error(f"El servidor no está disponible en la URL: {url} después de {max_retries} intentos.")

if __name__ == "__main__":
    asyncio.run(main())
