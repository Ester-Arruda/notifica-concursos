import logging

from sqlalchemy.orm import Session

from app.schemas import ScraperRunResult
from app.scraper.pci import buscar_concursos
from app.services import cleanup_service, filter_service, notification_service, email_service

logger = logging.getLogger(__name__)


def executar_monitoramento(db: Session) -> ScraperRunResult:
    # 1. limpeza dos registros antigos (RN16)
    cleanup_service.limpar_notificacoes_antigas(db)

    # 2. filtros configurados pelo usuario
    filtros = filter_service.obter_filtros(db)

    # 3. busca no PCI Concursos
    concursos = buscar_concursos()

    # 5. aplica os filtros (secoes 7-11)
    concursos_filtrados = [
        c for c in concursos if filter_service.concurso_atende_filtros(c, filtros)
    ]

    # 6. descarta os ja notificados (secao 12/22) e salva os novos
    novos = []
    for concurso in concursos_filtrados:
        if notification_service.ja_notificado(db, concurso.url):
            continue
        notification_service.marcar_como_notificado(db, concurso.url)
        novos.append(concurso)

    # 7. e-mail consolidado (secao 23) - so envia se houver algo novo
    email_enviado = email_service.enviar_email_concursos(filtros.email, novos)

    resultado = ScraperRunResult(
        concursos_encontrados=len(concursos),
        concursos_novos=len(novos),
        email_enviado=email_enviado,
    )
    logger.info("Execucao concluida: %s", resultado)
    return resultado
