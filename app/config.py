from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Banco de dados
    database_url: str = "sqlite:///./concurso_monitor.db"
    turso_database_url: str | None = None
    turso_auth_token: str | None = None
    
    # Scraper
    pci_base_url: str = "https://www.pciconcursos.com.br/concursos/"
    retencao_dias: int = 90  # ~3 meses (RN16 / RF14)

    # E-mail
    resend_api_key: str = ""
    email_from: str = "Monitor de Concursos <notificacoes@seudominio.com>"

settings = Settings()
