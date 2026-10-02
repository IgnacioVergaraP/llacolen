"""
Tests del blueprint profesor: listado de alumnos y detalle.
"""


# -------- Listado de alumnos --------

def test_listar_alumnos_sin_token(client):
    resp = client.get("/api/profesor/alumnos")
    assert resp.status_code == 401


def test_listar_alumnos_como_alumno_403(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 403


def test_listar_alumnos_como_profesor(client, mock_auth):
    resp = client.get("/api/profesor/alumnos", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 4
    ids = [a["id"] for a in data]
    assert "u-alu-001" in ids
    assert "u-alu-002" in ids
    assert "u-alu-003" in ids
    assert "u-alu-004" in ids
    assert "u-pro-001" not in ids
    assert "u-gim-001" not in ids
    item = data[0]
    assert {"id", "nombre", "email"} <= set(item.keys())


def test_listar_alumnos_como_gimnasio(client, mock_auth):
    resp = client.get("/api/profesor/alumnos", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    assert len(resp.get_json()["data"]) >= 4


# -------- Perfil de alumno --------

def test_perfil_alumno_ok(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/perfil",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "perfil" in data
    assert "resumen" in data
    assert data["perfil"]["nombre"] == "Juan Pérez"
    assert data["perfil"]["imc"] is not None
    assert data["resumen"]["rutinas_activas"] == 3


def test_perfil_alumno_inexistente_404(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-999/perfil",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 404


def test_perfil_no_alumno_404(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-pro-001/perfil",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 404


# -------- Progreso de alumno --------

def test_progreso_alumno_ok(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/progreso",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "historial" in data
    assert "evolucion" in data
    assert isinstance(data["historial"], list)
    assert len(data["historial"]) > 0
    assert data["evolucion"] is not None
    assert "pr_historico" in data["evolucion"]


def test_progreso_alumno_sin_datos(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-004/progreso",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data["historial"], list)


def test_progreso_alumno_inexistente_404(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-999/progreso",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 404