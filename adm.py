import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, User, DATABASE_URL  # импорт моделей и конфигурации

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

email = "q@q.com"  # <- заменить на свой email

user = db.query(User).filter_by(email=email).first()
if not user:
    print(f"Пользователь с email {email} не найден")
else:
    user.is_admin = 1
    db.commit()
    print(f"Пользователь {email} теперь админ!")
