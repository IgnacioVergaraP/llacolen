"""
Fixtures específicas de tests de integración.

Requieren que estén seteadas las variables de entorno:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY
  - SUPABASE_JWT_SECRET (para el backend)
Si no están, los tests de integración se saltan automáticamente.
"""
import os
import pytest
import httpx

from app import create_app


# Marcamos todos los tests de esta carpeta con @pytest.mark.integration
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def supabase_credentials():
    """
    Devuelve las credenciales necesarias para pegarle a Supabase Auth.
    Si faltan, saltea el test.
    """
    url = os.getenv("SUPABASE_URL")
    anon = os.getenv("SUPABASE_ANON_KEY")
    if not url or not anon:
        pytest.skip("Faltan SUPABASE_URL o SUPABASE_ANON_KEY para tests de integración.")
    return {"url": url, "anon_key": anon}


@pytest.fixture
def login_real(supabase_credentials):
    """
    Devuelve una función login(email, password) que:
      - Hace POST al endpoint /auth/v1/token?grant_type=password de Supabase.
      - Devuelve el access_token.
    """
    url = supabase_credentials["url"]
    anon = supabase_credentials["anon_key"]

    def _login(email: str, password: str) -> str:
        resp = httpx.post(
            f"{url}/auth/v1/token?grant_type=password",
            headers={
                "apikey": anon,
                "Content-Type": "application/json",
            },
            json={"email": email, "password": password},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    return _login