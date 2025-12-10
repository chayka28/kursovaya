# main.py
import os
import uuid
import datetime
from typing import Optional

from fastapi import (
    FastAPI, Request, Response, Depends, Form, HTTPException
)
from fastapi import Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from sqlalchemy import (
    create_engine, Column, Integer, String,
    DateTime, ForeignKey, Text
)
from sqlalchemy.orm import (
    sessionmaker, declarative_base,
    relationship, Session
)

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -------------------------------------------------
# MODELS
# -------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    fullname = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    theses = relationship("Thesis", back_populates="author", cascade="all, delete")
    applications = relationship("Application", back_populates="user", cascade="all, delete")


class SessionToken(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)


class Thesis(Base):
    __tablename__ = "theses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    abstract = Column(Text)
    status = Column(String, default="submitted")   # submitted / accepted / rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    author = relationship("User", back_populates="theses")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)          # listener или speaker
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact = Column(String)                        # Telegram / контакт
    title = Column(String)                          # для спикера
    thesis = Column(Text)                           # для спикера
    interests = Column(Text)                        # для слушателя
    status = Column(String, default="pending")     # статус заявки
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="applications")



Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# FASTAPI APP
# -------------------------------------------------
app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# UTILS
# -------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password.encode("utf-8")[:72])


def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password.encode("utf-8")[:72], hashed)


def create_session(db: Session, user: User, remember: bool) -> str:
    token = str(uuid.uuid4())
    ttl = datetime.timedelta(days=30) if remember else datetime.timedelta(hours=2)
    expires = datetime.datetime.utcnow() + ttl

    s = SessionToken(token=token, user_id=user.id, expires_at=expires)
    db.add(s)
    db.commit()
    return token


def get_current_user(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get("session_token")
    if not token:
        return None

    s = db.query(SessionToken).filter_by(token=token).first()
    if not s or s.expires_at < datetime.datetime.utcnow():
        return None

    return db.query(User).filter_by(id=s.user_id).first()

# -------------------------------------------------
# AUTH
# -------------------------------------------------
class RegisterData(BaseModel):
    email: EmailStr
    fullname: str
    password: str


class LoginData(BaseModel):
    email: EmailStr
    password: str
    remember: Optional[bool] = False


class ResetRequest(BaseModel):
    email: EmailStr


class NewPassword(BaseModel):
    token: str
    new_password: str


@app.post("/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email).first():
        return JSONResponse({"message": "Пользователь уже существует"}, 400)

    user = User(
        email=data.email,
        fullname=data.fullname,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    return {"message": "Регистрация успешна"}


@app.post("/login")
async def login(data: LoginData, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        return JSONResponse({"message": "Неверный email или пароль"}, 401)

    token = create_session(db, user, bool(data.remember))
    response.set_cookie("session_token", token, httponly=True, samesite="lax")
    return {"message": "Вход выполнен"}


@app.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        db.query(SessionToken).filter_by(token=token).delete()
        db.commit()

    resp = RedirectResponse("/", 302)
    resp.delete_cookie("session_token")
    return resp

# -------------------------------------------------
# PASSWORD RESET
# -------------------------------------------------
@app.post("/reset-password")
async def reset_request(data: ResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user:
        return {"message": "Если email существует — ссылка отправлена"}

    token = str(uuid.uuid4())
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    db.add(PasswordReset(token=token, user_id=user.id, expires_at=expires))
    db.commit()

    print("RESET LINK:", f"http://localhost:8000/reset-confirm?token={token}")
    return {"message": "Если email существует — ссылка отправлена"}


@app.get("/reset-confirm", response_class=HTMLResponse)
async def reset_page(request: Request, token: str):
    return templates.TemplateResponse("reset.html", {"request": request, "token": token})


@app.post("/reset-confirm")
async def reset_confirm(data: NewPassword, db: Session = Depends(get_db)):
    r = db.query(PasswordReset).filter_by(token=data.token).first()
    if not r or r.expires_at < datetime.datetime.utcnow():
        raise HTTPException(400, "Неверный или просроченный токен")

    user = db.query(User).filter_by(id=r.user_id).first()
    user.password_hash = hash_password(data.new_password)

    db.delete(r)
    db.commit()
    return {"message": "Пароль изменён"}

# -------------------------------------------------
# PAGES
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/apply", response_class=HTMLResponse)
async def page_apply(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    already_applied = False
    if user:
        existing = db.query(Application).filter_by(user_id=user.id).first()
        already_applied = bool(existing)

    return templates.TemplateResponse(
        "apply.html",
        {"request": request, "user": user, "already_applied": already_applied}
    )


@app.get("/thesis", response_class=HTMLResponse)
async def thesis_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/", 302)
    return templates.TemplateResponse("thesis.html", {"request": request, "user": user})


@app.get("/profile", response_class=HTMLResponse)
async def page_profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=302)

    theses = db.query(Thesis).filter_by(user_id=user.id).all()
    applications = db.query(Application).filter_by(user_id=user.id).all()

    # Проверка на пустой список
    last_application = applications[-1] if applications else None

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "theses": theses,
            "applications": applications,
            "last_application": last_application
        }
    )

# -------------------------------------------------
# FORMS
# -------------------------------------------------
@app.post("/application/submit")
async def submit_application(data: dict = Body(...), request: Request = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    # Проверяем, подал ли уже заявку
    existing = db.query(Application).filter_by(user_id=user.id).first()
    if existing:
        return JSONResponse({"message": "Вы уже подали заявку. Статус можно отследить в профиле."}, status_code=400)

    # Сохраняем заявку
    a = Application(
        user_id=user.id,
        role=data.get("role"),
        full_name=data.get("full_name"),
        email=data.get("email"),
        contact=data.get("contact"),
        interests=data.get("interests") if data.get("role")=="listener" else None,
        title=data.get("title") if data.get("role")=="speaker" else None,
        thesis=data.get("thesis") if data.get("role")=="speaker" else None,
        status="pending"
    )

    db.add(a)
    db.commit()

    return {"message": "Заявка успешно отправлена"}


@app.post("/thesis/submit")
async def submit_thesis(
    title: str = Form(...),
    abstract: str = Form(""),
    request: Request = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(401)

    thesis = Thesis(
        user_id=user.id,
        title=title,
        abstract=abstract,
    )
    db.add(thesis)
    db.commit()
    return RedirectResponse("/profile", 302)

@app.post("/apply")
async def submit_application(data: dict = Body(...), request: Request = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    # Проверяем, есть ли уже заявка
    existing = db.query(Application).filter_by(user_id=user.id).first()
    if existing:
        return JSONResponse({"message": "Заявка уже подана"}, status_code=400)

    a = Application(
        user_id=user.id,
        title=f"{user.fullname} ({data.get('role')})",
        status="pending"
    )
    db.add(a)
    db.commit()

    return JSONResponse({"message": "Заявка успешно отправлена"})
