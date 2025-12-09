# main.py
import os
import uuid
import datetime
from typing import Optional

from fastapi import FastAPI, Request, Response, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

# -----------------------------------------
# CONFIG
# -----------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------------------
# SQLAlchemy
# -----------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -----------------------------------------
# MODELS
# -----------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    fullname = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    theses = relationship("Thesis", back_populates="author")
    applications = relationship("Application", back_populates="user")


class SessionToken(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User")


class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User")


class Thesis(Base):
    __tablename__ = "theses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    abstract = Column(Text)
    status = Column(String, default="submitted")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author = relationship("User", back_populates="theses")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    status = Column(String, default="pending")
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="applications")


Base.metadata.create_all(bind=engine)

# -----------------------------------------
# FASTAPI
# -----------------------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------
# SCHEMAS
# -----------------------------------------
class RegisterData(BaseModel):
    fullname: str
    email: EmailStr
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

# -----------------------------------------
# UTILS
# -----------------------------------------
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


def create_session(db: Session, user: User, remember: bool = False) -> str:
    token = str(uuid.uuid4())
    ttl = datetime.timedelta(days=30) if remember else datetime.timedelta(hours=2)
    expires = datetime.datetime.utcnow() + ttl
    s = SessionToken(token=token, user_id=user.id, expires_at=expires)
    db.add(s)
    db.commit()
    return token


def get_user_from_token(db: Session, token: Optional[str]) -> Optional[User]:
    if not token:
        return None
    s = db.query(SessionToken).filter_by(token=token).first()
    if not s:
        return None
    if s.expires_at < datetime.datetime.utcnow():
        db.delete(s)
        db.commit()
        return None
    return db.query(User).filter_by(id=s.user_id).first()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    return get_user_from_token(db, request.cookies.get("session_token"))

# -----------------------------------------
# PAGES
# -----------------------------------------
@app.get("/", response_class=HTMLResponse)
async def page_index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/about", response_class=HTMLResponse)
async def page_about(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@app.get("/apply", response_class=HTMLResponse)
async def page_apply(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("apply.html", {"request": request, "user": user})


@app.get("/contact", response_class=HTMLResponse)
async def page_contact(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("contact.html", {"request": request, "user": user})


@app.get("/menu", response_class=HTMLResponse)
async def page_menu(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("menu.html", {"request": request, "user": user})


@app.get("/members", response_class=HTMLResponse)
async def page_members(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("members.html", {"request": request, "user": user})


@app.get("/program", response_class=HTMLResponse)
async def page_program(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse("program.html", {"request": request, "user": user})


@app.get("/thesis", response_class=HTMLResponse)
async def page_thesis(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("thesis.html", {"request": request, "user": user})


@app.get("/profile", response_class=HTMLResponse)
async def page_profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=302)

    theses = db.query(Thesis).filter_by(user_id=user.id).all()
    applications = db.query(Application).filter_by(user_id=user.id).all()

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "theses": theses, "applications": applications}
    )

# -----------------------------------------
# AUTH
# -----------------------------------------
@app.post("/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email).first():
        return JSONResponse({"message": "Пользователь уже существует"}, status_code=400)

    u = User(
        email=data.email,
        fullname=data.fullname,
        password_hash=hash_password(data.password),
    )
    db.add(u)
    db.commit()
    return {"message": "Регистрация успешна"}


@app.post("/login")
async def login(data: LoginData, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        return JSONResponse({"message": "Неверный email или пароль"}, status_code=401)

    token = create_session(db, user, remember=bool(data.remember))
    response.set_cookie("session_token", token, httponly=True, samesite="lax")
    return {"message": "Вход выполнен"}


@app.get("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        s = db.query(SessionToken).filter_by(token=token).first()
        if s:
            db.delete(s)
            db.commit()

    res = RedirectResponse("/", status_code=302)
    res.delete_cookie("session_token")
    return res

# -----------------------------------------
# PASSWORD RESET
# -----------------------------------------
@app.post("/reset-password")
async def reset_request(data: ResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()

    if not user:
        return {"message": "Если email существует — ссылка отправлена"}

    token = str(uuid.uuid4())
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    r = PasswordReset(token=token, user_id=user.id, expires_at=expires)
    db.add(r)
    db.commit()

    print("RESET LINK →", f"http://localhost:8000/reset-confirm?token={token}")

    return {"message": "Если email существует — ссылка отправлена"}


@app.get("/reset-confirm", response_class=HTMLResponse)
async def reset_page(request: Request, token: str):
    return templates.TemplateResponse("reset.html", {"request": request, "token": token})


@app.post("/reset-confirm")
async def reset_confirm(data: NewPassword, db: Session = Depends(get_db)):
    r = db.query(PasswordReset).filter_by(token=data.token).first()

    if not r or r.expires_at < datetime.datetime.utcnow():
        return JSONResponse({"message": "Токен неверный или устарел"}, status_code=400)

    user = db.query(User).filter_by(id=r.user_id).first()
    user.password_hash = hash_password(data.new_password)

    db.delete(r)
    db.commit()

    return {"message": "Пароль успешно изменён"}

# -----------------------------------------
# FORMS: SUBMIT THESIS / APPLICATION
# -----------------------------------------
@app.post("/thesis/submit")
async def submit_thesis(
    title: str = Form(...),
    abstract: str = Form(""),
    request: Request = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    t = Thesis(user_id=user.id, title=title, abstract=abstract)
    db.add(t)
    db.commit()

    return RedirectResponse("/profile", status_code=302)


@app.post("/application/submit")
async def submit_application(
    title: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)

    a = Application(user_id=user.id, title=title)
    db.add(a)
    db.commit()

    return RedirectResponse("/profile", status_code=302)
