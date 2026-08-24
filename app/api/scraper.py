import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.schemas import ScraperRunResult
from app.services.scraper_run_service import executar_monitoramento

logger = logging.getLogger(__name__)

router = APIRouter(tags=["scraper"])

@router.api_route("/scraper/run", methods=["GET", "POST"], response_model=ScraperRunResult)
def run_scraper(db: Session = Depends(get_db)):
    try:
        return executar_monitoramento(db)
    except Exception:
        logger.exception("Erro durante a execucao do scraper.")
        raise HTTPException(status_code=500, detail="Erro ao executar o monitoramento.")
