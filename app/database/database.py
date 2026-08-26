"""
Configuracao da engine SQLAlchemy e da sessao do banco (SQLite),
conforme secao 13 do documento.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {}
db_url = settings.database_url

if settings.turso_database_url and settings.turso_auth_token:
    hostname = settings.turso_database_url.replace("libsql://", "")
    db_url = f"sqlite+libsql://{hostname}?secure=true"
    connect_args = {"auth_token": settings.turso_auth_token}
elif settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessao e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria as tabelas caso ainda nao existam."""
    from app.database import models
    Base.metadata.create_all(bind=engine)
