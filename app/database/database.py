"""
Configuracao da engine SQLAlchemy e da sessao do banco (SQLite),
conforme secao 13 do documento.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False e necessario porque o FastAPI/uvicorn pode
# acessar a conexao a partir de threads diferentes (SQLite por padrao
# so permite acesso pela thread que criou a conexao).
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

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
