from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio
import json

app = FastAPI()

# Serve static files (your HTML UI)
app.mount("/public", StaticFiles(directory="public"), name="public")

# Global variables to store current values
current_data = {
    "slider1": 0.5,
    "slider2": 0.3
}

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")
    
    # Start a task to send current data periodically
    async def send_data():
        while True:
            try:
                await websocket.send_text(json.dumps(current_data))
                await asyncio.sleep(0.033)  # ~30fps
            except:
                break
    
    # Start the sending task
    send_task = asyncio.create_task(send_data())
    
    try:
        # Listen for incoming messages from the UI
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                # Update current_data with any new values
                current_data.update(data)
                    
                print(f"Received from UI: {data}")
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        send_task.cancel()
        print("WebSocket client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)