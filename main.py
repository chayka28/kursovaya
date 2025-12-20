import os
import uuid
import datetime
from typing import Optional
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from fastapi import (
    FastAPI, Request, Response, Depends, Form, HTTPException, Body
)
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
    is_admin = Column(Integer, default=0)
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
    status = Column(String, default="submitted")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    author = relationship("User", back_populates="theses")

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact = Column(String)
    title = Column(String)
    thesis = Column(Text)
    interests = Column(Text)
    status = Column(String, default="pending")
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

    db.add(SessionToken(token=token, user_id=user.id, expires_at=expires))
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


def require_admin(user: User):
    if not user or not user.is_admin:
        raise HTTPException(403, "Access denied")

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
# PAGES
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "about.html",
        {"request": request, "user": user}
    )


@app.get("/program", response_class=HTMLResponse)
async def program(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "program.html",
        {"request": request, "user": user}
    )

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "user": user}
    )

@app.get("/apply", response_class=HTMLResponse)
async def apply_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    already_applied = False
    last_application = None

    if user:
        last_application = db.query(Application).filter_by(user_id=user.id).order_by(Application.submitted_at.desc()).first()
        already_applied = bool(last_application)

    return templates.TemplateResponse(
        "apply.html",
        {
            "request": request,
            "user": user,
            "already_applied": already_applied,
            "last_application": last_application
        }
    )

@app.get("/thesis", response_class=HTMLResponse)
async def thesis_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if not user:
        # Передаем None для неавторизованных пользователей
        return templates.TemplateResponse(
            "thesis.html",
            {"request": request, "user": None, "message": "Требуется авторизация для подачи заявки", "thesis_count": 0}
        )

    thesis_count = db.query(Thesis).filter_by(user_id=user.id).count()

    return templates.TemplateResponse(
        "thesis.html",
        {"request": request, "user": user, "thesis_count": thesis_count}
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=302)

    theses = db.query(Thesis).filter_by(user_id=user.id).all()
    last_application = db.query(Application).filter_by(user_id=user.id).order_by(Application.submitted_at.desc()).first()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "theses": theses,
            "last_application": last_application
        }
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if not user or not user.is_admin:
        raise HTTPException(status_code=403)

    applications = db.query(Application).order_by(Application.submitted_at.desc()).all()
    theses = db.query(Thesis).order_by(Thesis.created_at.desc()).all()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user,
            "applications": applications,
            "theses": theses
        }
    )

# -------------------------------------------------
# APPLICATION SUBMIT
# -------------------------------------------------

@app.post("/application/submit")
async def submit_application(
    request: Request,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "auth_required"}, status_code=401)

    # ❗ ОГРАНИЧЕНИЕ: 1 заявка
    existing = db.query(Application).filter_by(user_id=user.id).first()
    if existing:
        return JSONResponse(
            {"message": "Вы уже подали заявку"},
            status_code=400
        )

    app_obj = Application(
        user_id=user.id,
        role=data.get("role"),
        full_name=data.get("full_name"),
        email=data.get("email"),
        contact=data.get("contact"),
        title=data.get("title"),
        thesis=data.get("thesis"),
        interests=data.get("interests"),
        status="pending"
    )

    db.add(app_obj)
    db.commit()

    return {"message": "Заявка успешно отправлена"}


# -------------------------------------------------
#  THESIS SUBMIT
# -------------------------------------------------

@app.post("/thesis/submit")
async def submit_thesis(
    request: Request,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "auth_required"}, status_code=401)

    # Логика подачи тезиса
    count = db.query(Thesis).filter_by(user_id=user.id).count()
    if count >= 5:
        return JSONResponse(
            {"message": "Можно отправить не более 5 тезисов"},
            status_code=400
        )

    thesis = Thesis(
        user_id=user.id,
        title=data.get("title"),
        abstract=data.get("abstract"),
        status="submitted"
    )

    db.add(thesis)
    db.commit()

    return {"message": "Тезис успешно отправлен"}


# -------------------------------------------------
#  THESIS EDIT
# -------------------------------------------------

@app.get("/thesis/edit/{thesis_id}", response_class=HTMLResponse)
async def edit_thesis_page(request: Request, thesis_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Необходимо авторизоваться")

    thesis = db.query(Thesis).filter_by(id=thesis_id, user_id=user.id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Тезис не найден")

    return templates.TemplateResponse("edit_thesis.html", {"request": request, "thesis": thesis})

@app.post("/thesis/edit/{thesis_id}")
async def edit_thesis(
    thesis_id: int,
    title: str = Body(...),
    abstract: str = Body(...),
    db: Session = Depends(get_db)
):
    thesis = db.query(Thesis).filter_by(id=thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Тезис не найден")

    thesis.title = title
    thesis.abstract = abstract
    db.commit()

    return {"message": "Тезис успешно обновлен"}

@app.post("/thesis/delete/{thesis_id}")
async def delete_thesis(thesis_id: int, db: Session = Depends(get_db)):
    thesis = db.query(Thesis).filter_by(id=thesis_id).first()
    if not thesis:
        raise HTTPException(status_code=404, detail="Тезис не найден")

    db.delete(thesis)
    db.commit()

    return {"message": "Тезис успешно удален"}



# -------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403)

    applications = db.query(Application).order_by(Application.submitted_at.desc()).all()
    theses = db.query(Thesis).order_by(Thesis.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "user": user, "applications": applications, "theses": theses}
    )

@app.post("/admin/application/{app_id}/approve")
async def approve_application(app_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)

    app_obj = db.query(Application).filter_by(id=app_id).first()
    if not app_obj:
        raise HTTPException(404, detail="Заявка не найдена")

    app_obj.status = "approved"
    db.commit()
    return JSONResponse({"message": "Заявка одобрена"}, status_code=200)


@app.post("/admin/application/{app_id}/reject")
async def reject_application(app_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    
    app_obj = db.query(Application).filter_by(id=app_id).first()
    if not app_obj:
        raise HTTPException(404, detail="Заявка не найдена")

    app_obj.status = "rejected"
    db.commit()
    return {"message": "Заявка отклонена"}

@app.post("/admin/application/{application_id}/status")
async def update_application_status(
    application_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    require_admin(user)
    
    # Получаем данные из тела запроса
    data = await request.json()
    new_status = data.get("status")
    
    if not new_status:
        raise HTTPException(400, detail="Статус не указан")
    
    # Проверяем допустимые статусы
    allowed_statuses = ["pending", "approved", "rejected"]
    if new_status not in allowed_statuses:
        raise HTTPException(400, detail=f"Недопустимый статус. Допустимые: {allowed_statuses}")
    
    # Находим и обновляем заявку
    application = db.query(Application).filter_by(id=application_id).first()
    if not application:
        raise HTTPException(404, detail="Заявка не найдена")
    
    application.status = new_status
    db.commit()
    
    return {"message": f"Статус заявки обновлен на '{new_status}'"}


# -------------------------------------------------
# PDF DOWNLOADER
# -------------------------------------------------

@app.get("/download/program-pdf")
async def download_pdf():
    static_dir = "static"
    filename = "program.pdf"
    filepath = os.path.join(static_dir, filename)

    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # 🔹 Регистрируем Unicode-шрифт (ОБЯЗАТЕЛЬНО для кириллицы)
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "HeiseiMin-W3"
    styles["Title"].fontName = "HeiseiMin-W3"
    styles["Heading2"].fontName = "HeiseiMin-W3"

    content = []

    # Заголовок
    content.append(Paragraph("<b>Программа конференции CodeFuture 2025</b>", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("📅 <b>Даты проведения:</b> 10–12 мая 2025 г.", styles["Normal"]))
    content.append(Spacer(1, 20))

    # День 1
    content.append(Paragraph("<b>День 1 — 10 мая</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("10:00 — Открытие конференции (Zoom Hall 1)", styles["Normal"]))
    content.append(Paragraph("11:00 — Доклады секции «Web-технологии»", styles["Normal"]))
    content.append(Paragraph("13:00 — Перерыв", styles["Normal"]))
    content.append(Paragraph("14:00 — Доклады секции «AI и машинное обучение»", styles["Normal"]))
    content.append(Paragraph("17:00 — Круглый стол «IT-тренды 2025»", styles["Normal"]))
    content.append(Spacer(1, 20))

    # День 2
    content.append(Paragraph("<b>День 2 — 11 мая</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("10:00 — Кибербезопасность и защита данных", styles["Normal"]))
    content.append(Paragraph("12:00 — DevOps и облачные технологии", styles["Normal"]))
    content.append(Paragraph("14:00 — Практические кейсы индустрии", styles["Normal"]))
    content.append(Spacer(1, 20))

    # День 3
    content.append(Paragraph("<b>День 3 — 12 мая</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("11:00 — Панельная дискуссия", styles["Normal"]))
    content.append(Paragraph("13:00 — Подведение итогов и закрытие", styles["Normal"]))

    doc.build(content)

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="CodeFuture_2025_Program.pdf"
    )

# -------------------------------------------------
#  CONTACTS SUBMIT
# -------------------------------------------------

@app.post("/contact/submit")
async def submit_contact(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    if not data.get("name") or not data.get("email") or not data.get("message"):
        return JSONResponse(
            {"message": "Заполните все поля"},
            status_code=400
        )

    msg = ContactMessage(
        name=data["name"],
        email=data["email"],
        message=data["message"]
    )

    db.add(msg)
    db.commit()

    return {"message": "Сообщение отправлено"}
