"""
Tests del dashboard del profesor.
"""


def test_dashboard_sin_token(client):
    resp = client.get("/api/profesor/dashboard")
    assert resp.status_code == 401


def test_dashboard_como_alumno_403(client, mock_auth):
    resp = client.get("/api/profesor/dashboard", headers=mock_auth.as_alumno())
    assert resp.status_code == 403


def test_dashboard_como_profesor(client, mock_auth):
    resp = client.get("/api/profesor/dashboard", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "alumnos_activos_semana" in data
    assert "alumnos_total" in data
    assert "solicitudes_pendientes" in data
    assert data["alumnos_total"] == 4
    assert data["alumnos_activos_semana"] >= 1
    assert data["solicitudes_pendientes"] >= 0


def test_dashboard_como_gimnasio(client, mock_auth):
    resp = client.get("/api/profesor/dashboard", headers=mock_auth.as_admin())
    assert resp.status_code == 200