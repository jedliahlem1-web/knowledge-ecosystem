import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from crewai import Agent, Task, Crew, Process

app = FastAPI()

# خدمة الملفات الثابتة (واجهة المستخدم)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>منظومة الوكلاء النخبويين تعمل بنجاح</h1>"

# ==========================================
# تعريف الوكلاء (بin ضمنهم الوكيلان الجديدان)
# ==========================================

# 1. وكيل البحث العام
researcher_agent = Agent(
    role='باحث رئيسي متقدم',
    goal='جمع أحدث المعلومات وتحليلها بدقة لضمان شمولية الأبحاث.',
    backstory='باحث محترف وخبير في استخراج البيانات الموثوقة وتحليلها.',
    verbose=True,
    allow_delegation=True
)

# 2. وكيل الهندسة الكهربائية والميكانيكية (جديد - يتعلم ويبحث بعمق)
electrical_mechanical_agent = Agent(
    role='خبير وباحث متقدم في الهندسة الكهربائية والميكانيكية',
    goal='إجراء أبحاث شاملة، وتحليل، وتعلم كل التفاصيل والابتكارات المتعلقة بالأنظمة الكهربائية، الدوائر، الميكانيكا، وتكامل الأجهزة.',
    backstory='مهندس وباحث محترف مخصص لاستكشاف وفهم وتطوير الأنظمة الكهربائية والميكانيكية وتحديث معرفتك باستمرار.',
    verbose=True,
    allow_delegation=True
)

# 3. وكيل علم الأحياء والتقنية الحيوية (جديد - يتعلم ويبحث بعمق)
biology_agent = Agent(
    role='خبير وباحث متقدم في علم الأحياء والتقنية الحيوية',
    goal='البحث والتققصي المستمر في التفاعلات البيولوجية، الكيمياء الحيوية، والعلوم الحيوية لفهم وتحليل كافة تفاصيل التخصص.',
    backstory='باحث متميز في علم الأحياء والأنظمة الحيوية، مهمتك التعلم المستمر وتحليل العمليات الحيوية وتقديم رؤى علمية دقيقة.',
    verbose=True,
    allow_delegation=True
)

# ==========================================
# مسار الـ WebSocket للتواصل المباشر مع الواجهة
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_prompt = message_data.get("prompt", "مهمة بحثية جديدة")
            
,            await websocket.send_text(json.dumps({"status": "info", "message": "تم استلام المهمة وجاري تشغيل الوكلاء..."}))
            
            # تحديد المهام للوكلاء بناءً على المدخلات
            task_research = Task(
                description=f'إجراء بحث شامل حول: {user_prompt}',
                expected_output='تقرير بحثي أولي مفصل.',
                agent=researcher_agent
            )
            
            task_eng = Task(
                description=f'دراسة الجوانب الهندسية (الكهربائية والميكانيكية) وتحليل المكونات المرتبطة بـ: {user_prompt}',
                expected_output='تقرير هندسي تقني تفصيلي.',
                agent=electrical_mechanical_agent
            )
            
            task_bio = Task(
                description=f'تحليل الجوانب الحيوية والبيولوجية والتقنية الحيوية المرتبطة بـ: {user_prompt}',
                expected_output='تقرير علمي حيوي متكامل.',
                agent=biology_agent
            )
            
            # تجميع الفريق وبدء التنفيذ
            crew = Crew(
                agents=[researcher_agent, electrical_mechanical_agent, biology_agent],
                tasks=[task_research, task_eng, task_bio],
                process=Process.sequential,
                verbose=True
            )
            
            # تنفيذ العمليات بشكل غير متزامن
            result = crew.kickoff()
            
            await websocket.send_text(json.dumps({
                "status": "complete", 
                "result": str(result)
            }))
            
    except WebSocketDisconnect:
        print("تم قطع الاتصال مع العميل")
