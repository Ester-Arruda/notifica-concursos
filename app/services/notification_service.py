from sqlalchemy.orm import Session

from app.database.models import ConcursoNotificado


def ja_notificado(db: Session, url: str) -> bool:
    return db.get(ConcursoNotificado, url) is not None


def marcar_como_notificado(db: Session, url: str) -> None:
    """Insere a URL na tabela. Idempotente: nao falha se ja existir."""
    if ja_notificado(db, url):
        return
    db.add(ConcursoNotificado(url=url))
    db.commit()
