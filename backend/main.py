from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

connected_clients = set()

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/api/today")
async def get_today():
    now = datetime.now()
    return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "title": "today's topic: what you think about ICE?",
            "rules": "no rules, just speak your mind!",
            "image_url": "/static/ice_image.jpg"

        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast received message to all clients
            await broadcast(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast(message: str):
    to_remove = []
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            # client is probably dead
            to_remove.append(client)

    for c in to_remove:
        connected_clients.remove(c)
