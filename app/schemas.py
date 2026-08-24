"""Schemas Pydantic (validacao/serializacao) usados pela API e pelo scraper."""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class FiltrosOut(BaseModel):
    """Retorno de GET /filters."""
    salario_minimo: Optional[float] = None
    estado: Optional[list[str]] = None
    email: Optional[str] = None

    model_config = {"from_attributes": True}


class FiltrosIn(BaseModel):
    """Corpo de PUT /filters. Todos os campos sao opcionais (RF10)."""
    salario_minimo: Optional[float] = Field(default=None, ge=0)
    estado: Optional[list[str]] = None
    email: Optional[EmailStr] = None


class Concurso(BaseModel):
    """Representacao em memoria de um concurso extraido do PCI (RN04)."""
    url: str
    titulo: str
    orgao: Optional[str] = None
    cargo: Optional[str] = None
    estado: Optional[str] = None
    salario: Optional[float] = None
    aberto: bool = True


class ScraperRunResult(BaseModel):
    """Retorno de POST /scraper/run."""
    concursos_encontrados: int
    concursos_novos: int
    email_enviado: bool
