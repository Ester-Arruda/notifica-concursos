from fastapi import APIRouter

from app.database.database import engine, Base
from app.database import models  # garante que os models estão registrados

router = APIRouter()


@router.post("/admin/reset-db")
def reset_db():
    """Apaga todos os dados e recria as tabelas vazias."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Banco de dados resetado com sucesso"}