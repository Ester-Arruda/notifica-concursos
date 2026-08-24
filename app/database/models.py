import datetime as dt

from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database.database import Base


class ConcursoNotificado(Base):
    __tablename__ = "concursos_notificados"

    url = Column(String, primary_key=True, index=True)
    data_adicionado = Column(DateTime, default=dt.datetime.utcnow, nullable=False)


class Filtros(Base):
    __tablename__ = "filtros"

    id = Column(Integer, primary_key=True)  # sempre 1, ver services/filter_service.py
    salario_minimo = Column(Float, nullable=True)
    estado = Column(String, nullable=True)
    email = Column(String, nullable=True)
