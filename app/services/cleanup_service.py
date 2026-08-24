"""
Service de limpeza (secao 16).

Remove da tabela concursos_notificados os registros com mais de
`settings.retencao_dias` (~3 meses), conforme RN16 / RF14 / RNF04.
"""
import datetime as dt
import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import ConcursoNotificado

logger = logging.getLogger(__name__)


def limpar_notificacoes_antigas(db: Session) -> int:
    """Deleta registros mais antigos que a retencao configurada. Retorna quantos foram removidos."""
    limite = dt.datetime.utcnow() - dt.timedelta(days=settings.retencao_dias)

    removidos = (
        db.query(ConcursoNotificado)
        .filter(ConcursoNotificado.data_adicionado < limite)
        .delete(synchronize_session=False)
    )
    db.commit()

    if removidos:
        logger.info("Limpeza: %d registro(s) removido(s) (retencao de %d dias).", removidos, settings.retencao_dias)

    return removidos
