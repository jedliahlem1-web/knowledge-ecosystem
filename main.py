import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from crewai import Agent, Task, Crew, Process

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

KNOWLEDGE_FILE = "continuous_knowledge_ledger.json"

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        try:
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "math_history": "بدايات الحساب والهندسة الإقليدية",
        "physics_history": "الميكانيكا الكلاسيكية لنيوتن",
        "chem_history": "الجدول الدوري والتفاعلات الأساسية",
        "bio_history": "علم الأحياء الخلوي والوراثة المندلية",
        "programming_history": "لغة الآلة وتطور Assembly و C و Python",
        "engineering_history": "الآلات البسيطة والدوائر الكهربائية الأوليّة"
    }

def save_knowledge(data):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>منظومة التعلم الذاتي التراكمي تعمل بنجاح تام</h1>"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_prompt = message_data.get("prompt", "بدء حلقة التعلم التراكمي واكتشاف الابتكارات")
            
            ledger = load_knowledge()
            
            await websocket.send_text(json.dumps({
                "status": "info", 
                "message": "🧠 بدأ فريق النخبة عمليات التعلم والتطوير في الخلفية، يرجى الانتظار..."
            }))
            
            # تعريف الوكلاء
            researcher_agent = Agent(role='باحث رئيسي ومنسق التعلم الذاتي', goal='متابعة حلقات التعلم المستمر وتوثيق الاكتشافات.', backstory='محلل استراتيجي.', verbose=True, allow_delegation=True)
            math_agent = Agent(role='عالم الرياضيات التطبيقية', goal='تطوير نماذج رياضية جديدة.', backstory='عالم رياضيات.', verbose=True, allow_delegation=True)
            physics_agent = Agent(role='فيزيائي النظريات', goal='تطوير قوانين ديناميكية جديدة.', backstory='فيزيائي.', verbose=True, allow_delegation=True)
            chemistry_agent = Agent(role='خبير الكيمياء التراكمية', goal='ابتكار مواد ومرشحات جديدة.', backstory='كيميائي.', verbose=True, allow_delegation=True)
            biology_agent = Agent(role='عالم الأحياء والطب', goal='ضمان الأمان الحيوي.', backstory='باحث طبي.', verbose=True, allow_delegation=True)
            programming_cyber_agent = Agent(role='مهندس البرمجيات والأمن السيبراني ومبتكر لغات البرمجة', goal='صياغة لغة برمجة جديدة ومحمية.', backstory='مبتكر لغات.', verbose=True, allow_delegation=True)
            electrical_mechanical_agent = Agent(role='خبير التكامل الهندسي', goal='تحويل النظريات لنماذج ملموسة.', backstory='مهندس.', verbose=True, allow_delegation=True)

            t_math = Task(description=f'بناءً على المعرفة ({ledger["math_history"]}): طوّر نموذجاً رياضياً لـ {user_prompt}', expected_output='نموذج رياضي.', agent=math_agent)
            t_prog = Task(description=f'بناءً على تاريخ اللغات ({ledger["programming_history"]}): صغ قواعد ونواة لغة البرمجة الجديدة لـ {user_prompt}', expected_output='قواعد اللغة البرمجية الجديدة.', agent=programming_cyber_agent)
            t_phys = Task(description=f'تحليل فيزيائي ديناميكي لـ {user_prompt}', expected_output='تحليل فيزيائي.', agent=physics_agent)
            t_chem = Task(description=f'ابتكار مادة أو مرشح نانوي لـ {user_prompt}', expected_output='تقرير كيميائي.', agent=chemistry_agent)
            t_bio = Task(description=f'معايير السلامة والتوافق الحيوي لـ {user_prompt}', expected_output='تقرير بيولوجي.', agent=biology_agent)
            t_eng = Task(description=f'تصميم هندسي ميكانيكي وكهربائي لـ {user_prompt}', expected_output='تصميم هندسي.', agent=electrical_mechanical_agent)
            t_res = Task(description=f'تجميع كافة النتائج وصياغة الورقة البحثية الكبرى لـ {user_prompt}', expected_output='تقرير شامل نهائي.', agent=researcher_agent)

            crew = Crew(
                agents=[math_agent, programming_cyber_agent, physics_agent, chemistry_agent, biology_agent, electrical_mechanical_agent, researcher_agent],
                tasks=[t_math, t_prog, t_phys, t_chem, t_bio, t_eng, t_res],
                process=Process.sequential,
                verbose=True
            )
            
            try:
                # تشغيل المهمة بشكل غير متزامن لعدم تجميد السيرفر
                result = await asyncio.to_thread(crew.kickoff)
                
                ledger["math_history"] += " -> تم دمج نموذج الرياضيات"
                ledger["programming_history"] += " -> تم تحديث لغة البرمجة"
                save_knowledge(ledger)
                
                await websocket.send_text(json.dumps({
                    "status": "complete", 
                    "result": str(result)
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "status": "complete", 
                    "result": f"⚠️ تنبيه من النظام: حدث خطأ أثناء تشغيل الوكلاء (تأكد من صلاحية مفتاح OpenAI API): {str(e)}"
                }))
            
    except WebSocketDisconnect:
        print("تم قطع الاتصال")
