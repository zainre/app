from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Chat instance
def get_ai_chat():
    return LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id="poetry_explanation",
        system_message="أنت خبير في الشعر العربي واللغة العربية. مهمتك شرح معاني الكلمات العربية والتراكيب الشعرية بطريقة واضحة ومفصلة. اشرح المعنى اللغوي والسياق الشعري والبلاغة إن وجدت."
    ).with_model("openai", "gpt-4o-mini")

# Define Models
class Poet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    bio: str
    era: str  # جاهلي، أموي، عباسي، أندلسي، حديث
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    image_url: Optional[str] = None

class Poem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    poet_id: str
    poet_name: str
    content: str  # النص الكامل
    theme: str  # غزل، مدح، رثاء، حكمة، وصف
    meter: Optional[str] = None  # البحر الشعري
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WordExplanation(BaseModel):
    word: str
    context: str  # الجملة أو البيت الذي جاءت فيه الكلمة
    explanation: str

class WordExplanationRequest(BaseModel):
    word: str
    context: str
    poem_title: Optional[str] = None
    poet_name: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    favorites: List[str] = []  # poem IDs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if key.endswith('_at') and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value)
                except:
                    pass
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "مرحباً بك في منصة الشعر العربي"}

# Poets routes
@api_router.get("/poets", response_model=List[Poet])
async def get_poets():
    poets = await db.poets.find().to_list(1000)
    return [Poet(**poet) for poet in poets]

@api_router.get("/poets/{poet_id}", response_model=Poet)
async def get_poet(poet_id: str):
    poet = await db.poets.find_one({"id": poet_id})
    if not poet:
        raise HTTPException(status_code=404, detail="الشاعر غير موجود")
    return Poet(**poet)

@api_router.post("/poets", response_model=Poet)
async def create_poet(poet: Poet):
    poet_dict = prepare_for_mongo(poet.dict())
    await db.poets.insert_one(poet_dict)
    return poet

# Poems routes
@api_router.get("/poems", response_model=List[Poem])
async def get_poems(poet_id: Optional[str] = None, theme: Optional[str] = None):
    query = {}
    if poet_id:
        query["poet_id"] = poet_id
    if theme:
        query["theme"] = theme
    
    poems = await db.poems.find(query).to_list(1000)
    return [Poem(**parse_from_mongo(poem)) for poem in poems]

@api_router.get("/poems/{poem_id}", response_model=Poem)
async def get_poem(poem_id: str):
    poem = await db.poems.find_one({"id": poem_id})
    if not poem:
        raise HTTPException(status_code=404, detail="القصيدة غير موجودة")
    return Poem(**parse_from_mongo(poem))

@api_router.post("/poems", response_model=Poem)
async def create_poem(poem: Poem):
    poem_dict = prepare_for_mongo(poem.dict())
    await db.poems.insert_one(poem_dict)
    return poem

# AI Word Explanation
@api_router.post("/explain-word", response_model=WordExplanation)
async def explain_word(request: WordExplanationRequest):
    try:
        # تحضير السياق للذكاء الاصطناعي
        context_info = f"الكلمة: {request.word}\n"
        context_info += f"السياق: {request.context}\n"
        if request.poem_title:
            context_info += f"القصيدة: {request.poem_title}\n"
        if request.poet_name:
            context_info += f"الشاعر: {request.poet_name}\n"
        
        prompt = f"""
        {context_info}
        
        يرجى شرح معنى الكلمة المحددة في سياقها الشعري. اذكر:
        1. المعنى اللغوي للكلمة
        2. المعنى في السياق الشعري
        3. أي إشارات بلاغية أو أدبية إن وجدت
        
        اجعل الشرح مختصر وواضح (لا يتجاوز 150 كلمة).
        """
        
        chat = get_ai_chat()
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return WordExplanation(
            word=request.word,
            context=request.context,
            explanation=response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في شرح الكلمة: {str(e)}")

# Search
@api_router.get("/search")
async def search(q: str):
    # البحث في الشعراء والقصائد
    poets = await db.poets.find({"name": {"$regex": q, "$options": "i"}}).to_list(10)
    poems = await db.poems.find({
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"poet_name": {"$regex": q, "$options": "i"}}
        ]
    }).to_list(20)
    
    return {
        "poets": [Poet(**poet) for poet in poets],
        "poems": [Poem(**parse_from_mongo(poem)) for poem in poems]
    }

# Initialize sample data
@api_router.post("/init-data")
async def init_sample_data():
    # إضافة شعراء عينة
    sample_poets = [
        {
            "id": str(uuid.uuid4()),
            "name": "أبو الطيب المتنبي",
            "bio": "أحد أعظم شعراء العربية، عُرف بفصاحته وحكمته وعزة نفسه. وُلد في الكوفة وعاش في القرن الرابع الهجري.",
            "era": "عباسي",
            "birth_year": 915,
            "death_year": 965,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "امرؤ القيس",
            "bio": "شاعر جاهلي، يُعتبر من أصحاب المعلقات السبع. عُرف بشعر الغزل والوصف والحماسة.",
            "era": "جاهلي",
            "birth_year": 501,
            "death_year": 544,
            "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face"
        }
    ]
    
    # إضافة قصائد عينة
    sample_poems = [
        {
            "id": str(uuid.uuid4()),
            "title": "على قدر أهل العزم",
            "poet_id": sample_poets[0]["id"],
            "poet_name": "أبو الطيب المتنبي",
            "content": """على قدر أهل العزم تأتي العزائم
وتأتي على قدر الكرام المكارم
وتعظم في عين الصغير صغارها
وتصغر في عين العظيم العظائم""",
            "theme": "حكمة",
            "meter": "الطويل"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "قفا نبك من ذكرى حبيب ومنزل",
            "poet_id": sample_poets[1]["id"],
            "poet_name": "امرؤ القيس",
            "content": """قفا نبك من ذكرى حبيب ومنزل
بسقط اللوى بين الدخول فحومل
فتوضح فالمقراة لم يعف رسمها
لما نسجتها من جنوب وشمأل""",
            "theme": "غزل",
            "meter": "الطويل"
        }
    ]
    
    # حفظ البيانات
    await db.poets.insert_many(sample_poets)
    await db.poems.insert_many(sample_poems)
    
    return {"message": "تم إنشاء البيانات التجريبية بنجاح"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()