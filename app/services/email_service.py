"""
Notificacao por e-mail (secao 23).

- Um unico e-mail consolidado por execucao, so enviado se houver pelo
  menos um concurso novo.
- O conteudo usa os dados extraidos do PCI NESTA execucao (o banco nao
  e usado para montar o e-mail - RN05/secao 23).
- O provedor usado aqui e o Resend (https://resend.com). Para trocar de
  provedor, so este arquivo precisa mudar (RNF03).
"""
import logging
from typing import Optional

import resend

from app.config import settings
from app.schemas import Concurso

logger = logging.getLogger(__name__)

resend.api_key = settings.resend_api_key


def _formatar_salario(salario: Optional[float]) -> str:
    if salario is None:
        return "Nao informado"
    return f"R$ {salario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _montar_html(concursos: list[Concurso]) -> str:
    blocos = []
    for c in concursos:
        localizacao = " / ".join(filter(None, [c.estado])) or "Local nao informado"
        blocos.append(f"""
        <tr>
          <td style="padding:16px 0;border-bottom:1px solid #e5e5e5;">
            <div style="font-size:16px;font-weight:600;color:#111;">{c.orgao or c.titulo}</div>
            <div style="font-size:14px;color:#333;margin-top:2px;">{c.cargo or ''}</div>
            <div style="font-size:13px;color:#666;margin-top:4px;">
              {_formatar_salario(c.salario)} &middot; {localizacao}
            </div>
            <div style="margin-top:8px;">
              <a href="{c.url}" style="color:#2563eb;text-decoration:none;font-size:14px;">Ver concurso &rarr;</a>
            </div>
          </td>
        </tr>
        """)

    return f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;background:#f5f5f5;padding:24px;">
        <table role="presentation" width="100%" style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;">
          <tr>
            <td style="padding:20px 24px;background:#111;color:#fff;font-size:18px;font-weight:600;">
              {len(concursos)} GATAAH ATENTAH! NOVOS CONCURSOOOS!!
            </td>
          </tr>
          <tr>
            <td style="padding:0 24px;">
              <table role="presentation" width="100%">
                {''.join(blocos)}
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """


def enviar_email_concursos(destinatario: str, concursos: list[Concurso]) -> bool:
    """
    Envia o e-mail consolidado. Retorna True se enviado, False se nao
    havia nada a enviar (lista vazia) - secao 23: "se nenhum concurso
    novo for encontrado, nao enviar e-mail".
    """
    if not concursos:
        logger.info("Nenhum concurso novo: e-mail nao sera enviado.")
        return False

    if not destinatario:
        logger.warning("E-mail de destino nao configurado; nao foi possivel notificar.")
        return False

    assunto = f"\U00002B50 {len(concursos)} CONCURSOS SAINDO DO FORNOOO"

    try:
        resend.Emails.send({
            "from": settings.email_from,
            "to": [destinatario],
            "subject": assunto,
            "html": _montar_html(concursos),
        })
    except Exception:
        logger.exception("Falha ao enviar e-mail de notificacao.")
        return False

    logger.info("E-mail enviado para %s com %d concurso(s).", destinatario, len(concursos))
    return True
