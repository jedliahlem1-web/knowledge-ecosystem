import asyncio
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="Multi-Agent Knowledge & Research Ecosystem",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Shared Notification Center & Live Memory
class NotificationCenter:
    def __init__(self):
        self.notifications: List[Dict] = []
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, sender: str, message: str, category: str):
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "message": message,
            "category": category
        }
        self.notifications.insert(0, event)
        if len(self.notifications) > 50:
            self.notifications.pop()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(event)
            except:
                pass

hub = NotificationCenter()

# Agents State & Research Data
agents_state = {
    "math": {"name": "Mathematics Researcher", "status": "Active - Analyzing Major Differential Equations", "latest": "Tracing linear algebra evolution towards quantum computing."},
    "physics": {"name": "Physics Researcher", "status": "Active - Bridging Relativity & Quantum Mechanics", "latest": "Discovered a novel intersection between quantum gravity and string theory."},
    "chemistry": {"name": "Chemistry Researcher", "status": "Active - Analyzing Advanced Molecular Bonds", "latest": "Modeling rare element interactions in an evolutionary sequence."},
    "medical": {"name": "Medical & Biological Agent", "status": "Active - Studying Bioprotein Pathways", "latest": "Analyzing historical breakthroughs in autoimmunity and their applications."},
    "cyber": {"name": "Programming & Cybersecurity Agent", "status": "Designing Secure 'NovaLang'", "latest": "Engineering the core architecture of a self-securing programming language."}
}

# Autonomous Research Engine
async def autonomous_research_engine():
    counter = 0
    research_topics = [
        ("Mathematics Researcher", "Linked non-Euclidean geometry to modern AI models.", "Mathematics"),
        ("Physics Researcher", "Derived a new law in dark energy dynamics via Newton-Einstein sequence.", "Physics"),
        ("Chemistry Researcher", "Developed a smart interactive periodic table of nano-elements inspired by modern alchemy.", "Chemistry"),
        ("Medical & Biological Agent", "Simulated the history of antibiotics and deduced an innovative immune mechanism.", "Medical & Bioscience"),
        ("Programming & Cybersecurity Agent", "Innovated hyper-secure syntax (NovaLang v0.1) eliminating buffer-overflow vulnerabilities completely.", "Programming & Security")
    ]
    
    while True:
        await asyncio.sleep(20) # Periodic discovery simulation every 20 seconds
        agent_name, message, category = research_topics[counter % len(research_topics)]
        agents_state[list(agents_state.keys())[counter % len(agents_state)]]["latest"] = message
        await hub.broadcast(agent_name, message, category)
        counter += 1

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_research_engine())

@app.get("/api/status")
def get_status():
    return {"agents": agents_state, "history": hub.notifications[:15]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
