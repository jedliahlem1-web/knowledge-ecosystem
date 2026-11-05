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

# ملف الذاكرة التراكمية لحفظ تاريخ التعلم المستمر
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

# ==========================================
# تعريف الوكلاء النخبويين للتعلم التراكمي المستمر
# ==========================================

researcher_agent = Agent(
    role='باحث رئيسي ومنسق التعلم الذاتي',
    goal='متابعة حلقات التعلم المستمر بين جميع الوكلاء وتوثيق الاكتشافات العابرة للتخصصات.',
    backstory='محلل استراتيجي يسجل التطور التراكمي للعلوم ويتحقق من الترابط بين التخصصات.',
    verbose=True,
    allow_delegation=True
)

math_agent = Agent(
    role='عالم الرياضيات التطبيقية والتعلم التراكمي التاريخي',
    goal='دراسة التطور التاريخي للرياضيات، البناء على أبحاث العلماء السابقين، وابتكار نماذج رياضية جديدة لم تحل من قبل.',
    backstory='عالم رياضيات يدرس كيف استكمل كل عالم أبحاث من سبقه، ويسعى لحل الفجوات الحسابية والمعادلات المعقدة.',
    verbose=True,
    allow_delegation=True
)

physics_agent = Agent(
    role='فيزيائي النظريات والتعلم المستمر',
    goal='تتبع تاريخ الفيزياء من الميكانيكا الكلاسيكية إلى الكم، وتطوير قوانين ديناميكية جديدة للتحكم بالطاقة.',
    backstory='فيزيائي متخصص في دراسة تسلسل الاكتشافات النظرية وتجاوز حدود المعرفة الفيزيائية الحالية.',
    verbose=True,
    allow_delegation=True
)

chemistry_agent = Agent(
    role='خبير الكيمياء التراكمية وعلم المواد المتقدم',
    goal='دراسة تطور المواد والمرشحات كيميائياً عبر التاريخ، واكتشاف مرشحات ومواد جديدة ذاتية الإصلاح والترشيح.',
    backstory='كيميائي يربط بين التاريخ الكيميائي وتطبيقات النانو التكنولوجية والحلول غير المسبوقة.',
    verbose=True,
    allow_delegation=True
)

biology_agent = Agent(
    role='عالم الأحياء والطب التراكمي',
    goal='متابعة التطور التاريخي للعلوم الطبية والوراثية لضمان التوافق الحيوي والأمان التام للأنظمة البشرية.',
    backstory='باحث طبي يدرس تطور فهم جسم الإنسان لتقديم معايير صحية آمنة ومبتكرة.',
    verbose=True,
    allow_delegation=True
)

programming_cyber_agent = Agent(
    role='مهندس البرمجيات، الأمن السيبراني، ومبتكر لغات البرمجة',
    goal='دراسة نشأة لغات البرمجة، معالجة ثغرات الأمان السيبراني تاريخياً، وصياغة وتطوير لغة برمجة جديدة كلياً خالية من الثغرات ومخصصة للذكاء الاصطناعي.',
    backstory='مبتكر لغات برمجية وخبراء أمن سيبراني، مهمته تأسيس لغة برمجة ذات جيل جديد بناءً على تاريخ تطوير Software Development.',
    verbose=True,
    allow_delegation=True
)

electrical_mechanical_agent = Agent(
    role='خبير التراكم الهندسي والتكامل الميكانيكي',
    goal='تحويل النظريات المبتكرة من باقي الوكلاء إلى نماذج هندسية ملموسة وتصاميم ميكانيكية وكهربائية ذكية.',
    backstory='مهندس يجمع بين التراث الهندسي البشري وأحدث تقنيات التصنيع والتكامل الذكي.',
    verbose=True,
    allow_delegation=True
)

# ==========================================
# مسار الاتصال المباشر الـ WebSocket
# ==========================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_prompt = message_data.get("prompt", "بدء حلقة التعلم التراكمي واكتشاف الابتكارات")
            
            # تحميل سجل المعرفة الحالي
            ledger = load_knowledge()
            
            await websocket.send_text(json.dumps({
                "status": "info", 
                "message": "🧠 تفعيل بروتوكول التعلم التراكمي المستمر! يجري الآن دمج تاريخ العلوم لابتكار حلول ولغة برمجة جديدة..."
            }))
            
            # صياغة المهام التراكمية
            t_math = Task(
                description=f'بناءً على المعرفة السابقة ({ledger["math_history"]})، ادرس النقطة التاريخية التالية، وطوّر قانوناً أو نموذجاً رياضياً جديداً يدعم: {user_prompt}',
                expected_output='إنجاز رياضي تراكمي ونموذج حسابي مبتكر.',
                agent=math_agent
            )
            
            t_prog = Task(
                description=f'بناءً على تاريخ اللغات ({ledger["programming_history"]}) والامنية السيبرانية، صغ قواعد ومفاهيم النواة للغة البرمجة الجديدة والمحمية سيبرانياً والمخصصة لـ: {user_prompt}',
                expected_output='قواعد النحو والأنماط الأساسية للغة البرمجة الجديدة وإنجاز أمني استثنائي.',
                agent=programming_cyber_agent
            )
            
            t_phys = Task(
                description=f'تطوير فهم فيزيائي جديد مبني على القوانين الحالية لدعم: {user_prompt}',
                expected_output='تحليل فيزيائي ديناميكي مبتكر.',
                agent=physics_agent
            )
            
            t_chem = Task(
                description=f'ابتكار مادة كيميائية أو مرشح نانوي متطور لدعم المشروع: {user_prompt}',
                expected_output='تقرير الكيمياء والمواد المبتكرة.',
                agent=chemistry_agent
            )
            
            t_bio = Task(
                description=f'تحدديد معايير السلامة والتوافق البيولوجي الجيني والتنفسي لـ: {user_prompt}',
                expected_output='تقرير الأمان الحيوي والطب التراكمي.',
                agent=biology_agent
            )
            
            t_eng = Task(
                description=f'دمج الابتكارات السابقة في نموذج هندسي ميكانيكي وكهربائي متكامل لـ: {user_prompt}',
                expected_output='تصميم هندسي متكامل للنموذج الأولي.',
                agent=electrical_mechanical_agent
            )
            
            t_res = Task(
                description=f'تجميع كافة الإنجازات الاستثنائية وتلخيص الورقة البحثية الشاملة واختراع لغة البرمجة لـ: {user_prompt}',
                expected_output='تقرير استثنائي شامل يبرز الإنجاز المبتكر لكل وكيل.',
                agent=researcher_agent
            )
            
            crew = Crew(
                agents=[
                    math_agent, 
                    programming_cyber_agent, 
                    physics_agent, 
                    chemistry_agent, 
                    biology_agent, 
                    electrical_mechanical_agent, 
                    researcher_agent
                ],
                tasks=[t_math, t_prog, t_phys, t_chem, t_bio, t_eng, t_res],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # تحديث وتحديث سجل المعرفة للتكرار القادم
            ledger["math_history"] += " -> تم دمج نموذج الرياضيات المتقدم"
            ledger["programming_history"] += " -> تم صياغة الجيل الجديد للغة البرمجة والمُحكم سيبرانياً"
            save_knowledge(ledger)
            
            await websocket.send_text(json.dumps({
                "status": "complete", 
                "result": str(result)
            }))
            
    except WebSocketDisconnect:
        print("تم قطع الاتصال")
