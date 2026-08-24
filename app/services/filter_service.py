from app.schemas import Concurso, FiltrosIn, FiltrosOut
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import Filtros
from app.schemas import Concurso, FiltrosIn

FILTROS_ID = 1


def filtros_para_saida(filtros: Filtros) -> FiltrosOut:
    return FiltrosOut(
        salario_minimo=filtros.salario_minimo,
        estado=(
            filtros.estado.split(",")
            if filtros.estado
            else None
        ),
        email=filtros.email,
    )


def obter_filtros(db: Session) -> Filtros:
    filtros = db.get(Filtros, FILTROS_ID)
    if filtros is None:
        filtros = Filtros(id=FILTROS_ID)
        db.add(filtros)
        db.commit()
        db.refresh(filtros)
    return filtros


def atualizar_filtros(db: Session, dados: FiltrosIn) -> Filtros:
    filtros = obter_filtros(db)
    filtros.salario_minimo = dados.salario_minimo
    if dados.estado:
        filtros.estado = ",".join(
            estado.upper().strip()
            for estado in dados.estado
        )
    else:
        filtros.estado = None
    filtros.email = dados.email
    db.commit()
    db.refresh(filtros)
    return filtros


def _normaliza(texto: Optional[str]) -> Optional[str]:
    return texto.strip().lower() if texto else None


def concurso_atende_filtros(concurso: Concurso, filtros: Filtros) -> bool:
    if filtros.salario_minimo is not None:
        if concurso.salario is None or concurso.salario < filtros.salario_minimo:
            return False

    if concurso.estado != None:
        if filtros.estado:
            estados_normalizados = {
                _normaliza(estado)
                for estado in filtros.estado.split(",")
            }

            if _normaliza(concurso.estado) not in estados_normalizados:
                return False

    return True
