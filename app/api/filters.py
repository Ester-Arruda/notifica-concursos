"""Endpoints GET /filters e PUT /filters (secao 19)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas import FiltrosIn, FiltrosOut
from app.services import filter_service

router = APIRouter(tags=["filters"])


@router.get("/filters", response_model=FiltrosOut)
def get_filters(db: Session = Depends(get_db)):
    """Retorna os filtros atuais."""
    filtros = filter_service.obter_filtros(db)
    return filter_service.filtros_para_saida(filtros)


@router.put("/filters", response_model=FiltrosOut)
def put_filters(dados: FiltrosIn, db: Session = Depends(get_db)):
    """Atualiza os filtros."""
    filtros = filter_service.atualizar_filtros(db, dados)
    return filter_service.filtros_para_saida(filtros)