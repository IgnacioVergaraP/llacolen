"""
Tests de integración contra Supabase real.

Verifican el flujo completo:
  login real → token real → request real al backend con validación real de JWT.

Requieren:
  - SUPABASE_URL y SUPABASE_ANON_KEY en el entorno.
  - Los 6 usuarios de prueba ya creados en Supabase Auth (seed).
  - El backend configurado con SUPABASE_URL y JWKS accesible.

Se corren con:
    pytest -m integration
"""
import pytest


# -------- Alumno --------

def test_login_real_alumno_y_perfil(client, login_real):
    token = login_real("alumno@gimnasio.com", "alumno123")
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["email"] == "alumno@gimnasio.com"
    assert data["rol"] == "alumno"
    # Filtrado de notas_profesor para el propio alumno
    assert "notas_profesor" not in data


# -------- Profesor --------

def test_login_real_profesor_y_alumnos(client, login_real):
    token = login_real("profesor@gimnasio.com", "profe123")
    headers = {"Authorization": f"Bearer {token}"}

    # /me
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["data"]["rol"] == "profesor"

    # Endpoint protegido por rol profesor
    resp2 = client.get("/api/profesor/alumnos", headers=headers)
    assert resp2.status_code == 200
    assert isinstance(resp2.get_json()["data"], list)


# -------- Admin --------

def test_login_real_admin_y_profesores(client, login_real):
    token = login_real("admin@gimnasio.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/admin/profesores", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json()["data"], list)


# -------- Forbidden --------

def test_alumno_no_puede_acceder_endpoint_admin(client, login_real):
    token = login_real("alumno@gimnasio.com", "alumno123")
    resp = client.get(
        "/api/admin/profesores",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.get_json()["error"]["name"] == "Forbidden"