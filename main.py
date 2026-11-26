from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from database import engine, get_db
from models import Base, Contact
from dotenv import load_dotenv
import smtplib
import os
from fastapi.responses import RedirectResponse
from email.message import EmailMessage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.responses import RedirectResponse



app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
DATABASE_URL = "sqlite:///./portfolio.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

LocalSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


load_dotenv()

@app.get("/")
def home(request: Request, success: bool = False):

    theme = request.cookies.get("theme", "light")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "theme": theme,
            "success": success
        }
    )

@app.post("/toggle-theme")
def toggle_theme(request: Request):
    current_theme = request.cookies.get("theme", "light")

    new_theme = "dark" if current_theme == "light" else "light"

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="theme",
        value=new_theme,
        max_age=31536000,
        httponly=True,
        samesite="lax"
    )

    return response

@app.post("/contact")
def save_contact(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    new_contact = Contact(
        name=name,
        email=email,
        subject=subject,
        message=message
    )

    db.add(new_contact)
    db.commit()

    return RedirectResponse(
        url="/?success=true#contact",
        status_code=303
    )