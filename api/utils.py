import json
from fastapi import WebSocket

async def send_json(websocket: WebSocket, type: str, payload: dict):
    """
    Helper function to send JSON data to the client with robust error handling.
    Checks if the websocket is connected before sending.
    """
    try:
        if websocket.client_state.name == 'CONNECTED':
            await websocket.send_text(json.dumps({"type": type, "payload": payload}))
            return True
        else:
            print(f"⚠️ WebSocket not connected, cannot send {type}")
            return False
    except Exception as e:
        print(f"⚠️ Failed to send {type}: {e}")
        return False