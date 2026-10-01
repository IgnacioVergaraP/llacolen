import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar")

    # CORS
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200"
    ).split(",")

    # -------- Supabase --------
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

    # Algoritmo que usa Supabase para firmar sus JWT.
    # Fijo en HS256 porque Supabase lo firma así.
    SUPABASE_JWT_ALGORITHM = "HS256"

    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = "testing"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None):
    name = name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)