"""
Configuracoes da aplicacao, carregadas de variaveis de ambiente (.env).

Centralizar aqui evita espalhar os.getenv(...) pelo codigo e facilita
trocar valores (ex: URL do PCI, retencao em dias) em um unico lugar,
conforme RNF03 (manutencao).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Banco de dados
    database_url: str = "sqlite:///./concurso_monitor.db"

    # Scraper
    pci_base_url: str = "https://www.pciconcursos.com.br/concursos/"
    retencao_dias: int = 90  # ~3 meses (RN16 / RF14)

    # E-mail
    resend_api_key: str = ""
    email_from: str = "Monitor de Concursos <notificacoes@seudominio.com>"

    # Protecao simples do endpoint de execucao do scraper (chamado pelo cron)
    cron_secret: str = ""


settings = Settings()
