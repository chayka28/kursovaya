from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# Инициализация шаблонов Jinja2
templates = Jinja2Templates(directory=".")

# Монтируем статику на путь "/"
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Описываем формы, которые принимает сервер
class RegisterData(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class ResetData(BaseModel):
    email: EmailStr

@app.post("/register")
def register(data: RegisterData):
    return {"message": f"Пользователь {data.fullname} успешно зарегистрирован"}

@app.post("/login")
def login(data: LoginData):
    return {"message": f"Вход выполнен: {data.email}"}

@app.post("/reset-password")
def reset(data: ResetData):
    return {"message": f"Письмо отправлено на {data.email}"}

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Страница "О нас"
@app.get("/about", response_class=HTMLResponse)
async def get_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Страница "Контакты"
@app.get("/contact", response_class=HTMLResponse)
async def get_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# Страница "Программа"
@app.get("/program", response_class=HTMLResponse)
async def get_program(request: Request):
    return templates.TemplateResponse("program.html", {"request": request})

# Разрешаем запросы с твоего сайта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
