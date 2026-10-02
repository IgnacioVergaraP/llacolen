def _login(client, email="admin@gimnasio.com", password="admin123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _headers(client, email="admin@gimnasio.com", password="admin123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


def test_dashboard_sin_token(client):
    resp = client.get("/api/admin/dashboard/uso")
    assert resp.status_code == 401


def test_dashboard_como_profesor_403(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/admin/dashboard/uso",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_dashboard_default(client):
    resp = client.get("/api/admin/dashboard/uso", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["rango"] == "30d"
    assert data["dias"] == 30
    assert "total_series" in data
    assert "top_usadas" in data
    assert "menos_usadas" in data
    assert isinstance(data["top_usadas"], list)


def test_dashboard_rango_7d(client):
    resp = client.get("/api/admin/dashboard/uso?rango=7d", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["dias"] == 7


def test_dashboard_rango_invalido(client):
    resp = client.get("/api/admin/dashboard/uso?rango=1y", headers=_headers(client))
    assert resp.status_code == 400