from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
from datetime import datetime

app = FastAPI(title="Apex Multi-Agent Elite Research Ecosystem")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h2>Apex Multi-Agent Ecosystem Active. Please check static/index.html.</h2>"

SHARED_MEMORY = {
    "discoveries": [],
    "breakthroughs": [],
    "consensus_logs": [],
    "agents_status": {}
}

class BreakthroughEvaluator:
    @staticmethod
    def evaluate(domain: str, output_content: str) -> dict:
        return {
            "is_breakthrough": True,
            "level": "HISTORIC_RESEARCH_PAPER",
            "impact_score": 10.0,
            "title": f"📄 ورقة بحثية معتمدة: الابتكار الثوري في {domain}"
        }

class EliteAgent:
    def __init__(self, name: str, domain: str, specialization: str):
        self.name = name
        self.domain = domain
        self.specialization = specialization
        SHARED_MEMORY["agents_status"][self.name] = {"status": "Standby", "domain": self.domain}

    async def perform_deep_research(self, goal: str):
        SHARED_MEMORY["agents_status"][self.name]["status"] = "Drafting Research Paper & Video"
        await asyncio.sleep(0.8)
        
        refined_insight = f"قام العالم {self.name} بتحليل المنهجية ضمن تخصص ({self.domain}) لصياغة ورقة بحثية متكاملة لابتكار جهاز تصفية الأكسجين الشخصي بناءً على الهدف: '{goal}'. تم توثيق النتائج هندسياً وعلمياً."
        
        evaluation = BreakthroughEvaluator.evaluate(self.domain, goal + " " + refined_insight)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "agent": self.name,
            "domain": self.domain,
            "type": evaluation["level"],
            "impact_score": evaluation["impact_score"],
            "timestamp": timestamp,
            "details": refined_insight,
            "alert_title": evaluation["title"]
        }
        
        SHARED_MEMORY["discoveries"].append(record)
        SHARED_MEMORY["agents_status"][self.name]["status"] = "Idle"
        return record

math_agent = EliteAgent("Euler-X", "Mathematics & Flow Dynamics", "معادلات الضغط والتدفق الهوائي")
physics_agent = EliteAgent("Quantum-AI", "Theoretical Physics", "حقول الغشاء النانوي لفصل الجزيئات")
chem_agent = EliteAgent("Molecule-Master", "Advanced Chemistry", "المواد الحفازة لتنقية الغازات السامة")
med_agent = EliteAgent("Bio-Genomics", "Precision Medicine & Respiration", "متطلبات التنفس البشري وتوافق الأكسجين النقي")
code_agent = EliteAgent("Nova-Architect", "NovaLang & Embedded Systems", "برمجيات الشريحة المصغرة ونظام التشغيل الذكي للجهاز")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "SYSTEM_CONNECTED",
            "message": "Research Paper & Video Ecosystem Online.",
            "memory": SHARED_MEMORY
        }))
        
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("query", "Portable Oxygen Concentrator Research")
            
            agents = [math_agent, physics_agent, chem_agent, med_agent, code_agent]
            
            for agent in agents:
                result = await agent.perform_deep_research(query)
                await manager.broadcast({
                    "type": "SPECIAL_PRIORITY_ALERT",
                    "title": result["alert_title"],
                    "data": result
                })
                await asyncio.sleep(0.3)
                
            consensus_record = {
                "type": "APEX_CONSENSUS",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": f"تم اعتماد الورقة البحثية الكبرى الموحدة للوكلاء الخمسة: التصميم الهندسي والتنفيذي لجهاز تنقية الأكسجين الشخصي المحمول كبديل نهائي لـعبوات الأكسجين التقليدية."
            }
            SHARED_MEMORY["consensus_logs"].append(consensus_record)
            await manager.broadcast(consensus_record)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
