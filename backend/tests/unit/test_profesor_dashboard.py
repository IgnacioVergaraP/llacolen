def _login(client, email="profesor@gimnasio.com", password="profe123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _auth_headers(client, email="profesor@gimnasio.com", password="profe123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


def test_dashboard_sin_token(client):
    resp = client.get("/api/profesor/dashboard")
    assert resp.status_code == 401


def test_dashboard_como_alumno_403(client):
    token = _login(client, "alumno@gimnasio.com", "alumno123")
    resp = client.get(
        "/api/profesor/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_dashboard_como_profesor(client):
    resp = client.get("/api/profesor/dashboard", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "alumnos_activos_semana" in data
    assert "alumnos_total" in data
    assert "solicitudes_pendientes" in data
    assert data["alumnos_total"] == 4
    assert data["alumnos_activos_semana"] >= 1
    assert data["solicitudes_pendientes"] == 0


def test_dashboard_como_gimnasio(client):
    resp = client.get(
        "/api/profesor/dashboard",
        headers=_auth_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 200

