from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import hashlib

app = FastAPI()

# =======================
# ШАБЛОНЫ И СТАТИКА
# =======================
templates = Jinja2Templates(directory="templates")

app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# =======================
# МОДЕЛИ ДАННЫХ
# =======================
class RegisterData(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class ResetData(BaseModel):
    email: EmailStr

# =======================
# ХРАНИЛИЩЕ ПОЛЬЗОВАТЕЛЕЙ (ПАМЯТЬ)
# =======================
users_db: dict[str, dict] = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(request: Request):
    email = request.cookies.get("user_email")
    return users_db.get(email)

# =======================
# AUTH API
# =======================
@app.post("/register")
async def register(data: RegisterData):
    if data.email in users_db:
        return {"message": "Пользователь уже существует"}

    users_db[data.email] = {
        "email": data.email,
        "fullname": data.fullname,
        "password": hash_password(data.password)
    }

    return {"message": "Регистрация успешна"}

@app.post("/login")
async def login(data: LoginData, response: Response):
    user = users_db.get(data.email)
    if not user or user["password"] != hash_password(data.password):
        return {"message": "Неверный email или пароль"}

    response.set_cookie(
        key="user_email",
        value=user["email"],
        httponly=True
    )

    return {"message": "Вы вошли в аккаунт"}

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("user_email")
    return response

@app.post("/reset-password")
async def reset(data: ResetData):
    return {"message": "Если email существует — письмо отправлено"}

# =======================
# HTML СТРАНИЦЫ
# =======================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/program", response_class=HTMLResponse)
async def program(request: Request):
    return templates.TemplateResponse("program.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    return templates.TemplateResponse("apply.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/thesis", response_class=HTMLResponse)
async def thesis(request: Request):
    return templates.TemplateResponse("thesis.html", {
        "request": request,
        "user": get_user(request)
    })

@app.get("/members", response_class=HTMLResponse)
async def members(request: Request):
    return templates.TemplateResponse("members.html", {
        "request": request,
        "user": get_user(request)
    })

# =======================
# ПРОФИЛЬ
# =======================
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

# =======================
# CORS
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
