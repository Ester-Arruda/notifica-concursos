import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup, Tag

from app.config import settings
from app.schemas import Concurso

logger = logging.getLogger(__name__)


SELECTOR_ITEM = "div[data-url]"
ATTR_URL = "data-url"

SELECTORS_TITULO = [".ca > a"]
SELECTORS_ORGAO = [".ca > a"]
SELECTORS_CARGO = [".ca .cd"]
SELECTORS_LOCAL = [".ca .cc"]
SELECTORS_SALARIO = [".ca .cd"]
SELECTORS_DATA = [".ca .ce"]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; MonitorDeConcursos/1.0; "
        "+https://github.com/) uso pessoal - 1 execucao/dia"
    )
}

_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
}


def _primeiro_texto(item: Tag, seletores: list[str]) -> Optional[str]:
    """Retorna o texto do primeiro seletor que encontrar algo, ou None."""
    for seletor in seletores:
        el = item.select_one(seletor)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def _parse_salario(texto: Optional[str]) -> Optional[float]:
    """Converte 'R$ 5.416,20' -> 5416.20."""

    if not texto:
        return None

    match = re.search(r"R\$\s*([\d.]+,\d{2})", texto)

    if not match:
        return None

    bruto = match.group(1).replace(".", "").replace(",", ".")

    try:
        return float(bruto)
    except ValueError:
        return None


def _parse_local(texto: Optional[str]) -> Optional[str]:
    if not texto:
        return None

    texto = texto.strip()
    match = re.match(r"^(.*?)[\s/\-]+([A-Za-z]{2})$", texto)
    if match:
        uf = match.group(2).upper()
        if uf in _UFS:
            return uf

    if texto.upper() in _UFS:
        return texto.upper()

    return None


def _extrair_cargo(item: Tag) -> Optional[str]:
    cd = item.select_one(".ca .cd")

    if not cd:
        return None

    span = cd.find("span", recursive=False)

    if not span:
        return None

    textos = [
        texto.strip()
        for texto in span.find_all(string=True, recursive=False)
        if texto.strip()
    ]

    return " ".join(textos) or None


def _item_esta_aberto(item: Tag) -> bool:
    """RF03: identifica se o concurso ainda esta com inscricoes abertas."""
    texto = item.get_text(" ", strip=True).lower()
    return not any(marcador in texto for marcador in SELECTORS_DATA)


def _parse_item(item: Tag) -> Optional[Concurso]:
    url = item.get(ATTR_URL)

    if not url:
        return None

    titulo = _primeiro_texto(item, SELECTORS_TITULO) or ""
    orgao = _primeiro_texto(item, SELECTORS_ORGAO)

    cargo = _extrair_cargo(item)

    local_texto = _primeiro_texto(item, SELECTORS_LOCAL)
    salario_texto = _primeiro_texto(item, SELECTORS_SALARIO)

    estado = _parse_local(local_texto)
    salario = _parse_salario(salario_texto)

    aberto = _item_esta_aberto(item)

    return Concurso(
        url=url,
        titulo=titulo,
        orgao=orgao,
        cargo=cargo,
        estado=estado,
        salario=salario,
        aberto=aberto,
    )


def buscar_concursos() -> list[Concurso]:
    with httpx.Client(headers=HEADERS, timeout=90, follow_redirects=True) as client:
        resposta = client.get("https://www.pciconcursos.com.br/concursos/")
        resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "lxml")
    itens = soup.select(SELECTOR_ITEM)

    concursos: list[Concurso] = []
    for item in itens:
        try:
            concurso = _parse_item(item)
        except Exception:
            logger.exception("Falha ao processar um item de concurso; pulando.")
            continue
        if concurso is not None:
            concursos.append(concurso)

    logger.info("Scraper: %d concursos encontrados em %s", len(concursos), "alvo")
    return concursos

