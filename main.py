from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Jinja2 шаблоны
templates = Jinja2Templates(directory="templates")

# Статика
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# DATA MODELS
class RegisterData(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class ResetData(BaseModel):
    email: EmailStr

# API ENDPOINTS
@app.post("/register")
async def register(data: RegisterData):
    return {"message": f"Пользователь {data.fullname} зарегистрирован"}

@app.post("/login")
async def login(data: LoginData):
    return {"message": f"Вход выполнен: {data.email}"}

@app.post("/reset-password")
async def reset(data: ResetData):
    return {"message": f"Письмо отправлено: {data.email}"}

# HTML PAGES
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/program", response_class=HTMLResponse)
async def program(request: Request):
    return templates.TemplateResponse("program.html", {"request": request})

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/thesis", response_class=HTMLResponse)
async def thesis(request: Request):
    return templates.TemplateResponse("thesis.html", {"request": request})

@app.get("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.get("/members", response_class=HTMLResponse)
async def members(request: Request):
    return templates.TemplateResponse("members.html", {"request": request})

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
