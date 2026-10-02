"""
Tests del blueprint auth.

Con Supabase Auth:
  - Ya no hay POST /login (el login lo hace el frontend contra Supabase).
  - Solo existe GET /me, que valida el JWT y devuelve el perfil filtrado por rol.
"""


# -------- /api/auth/me --------

def test_me_sin_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.get_json()["error"]["name"] == "MissingToken"


def test_me_token_malformado(client):
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": "no-es-bearer"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["error"]["name"] == "InvalidAuthHeader"


def test_me_como_alumno(client, mock_auth):
    resp = client.get("/api/auth/me", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["email"] == "alumno@gimnasio.com"
    assert data["rol"] == "alumno"
    # Filtrado de notas_profesor:
    assert "notas_profesor" not in data
    # Sin password_hash (campo ya eliminado)
    assert "password_hash" not in data


def test_me_como_profesor(client, mock_auth):
    resp = client.get("/api/auth/me", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["rol"] == "profesor"
    # El profesor no tiene notas_profesor propias (es un campo del alumno)
    assert data.get("notas_profesor") is None


def test_me_como_admin(client, mock_auth):
    resp = client.get("/api/auth/me", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["rol"] == "gimnasio"


def test_me_usuario_inexistente(client, mock_auth):
    """Simular un token válido pero para un usuario que no existe en el repo."""
    # Forzamos un payload con un sub inválido
    headers = mock_auth._headers_con_payload({
        "sub": "u-no-existe",
        "email": "ghost@gimnasio.com",
        "app_metadata": {"rol": "alumno"},
    })
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 401
    assert resp.get_json()["error"]["name"] == "UserNotFound"