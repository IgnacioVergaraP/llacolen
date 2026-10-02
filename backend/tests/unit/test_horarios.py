"""
Tests del módulo de horarios (blueprint admin).
"""


_PAYLOAD = {
    "profesor_id": "u-pro-001",
    "dia_semana": 3,
    "hora_inicio": "14:00",
    "hora_fin": "18:00",
    "notas": "Turno tarde",
}


# -------- Listar --------

def test_listar_sin_token(client):
    resp = client.get("/api/admin/horarios")
    assert resp.status_code == 401


def test_listar_como_profesor_403(client, mock_auth):
    resp = client.get("/api/admin/horarios", headers=mock_auth.as_profesor())
    assert resp.status_code == 403


def test_listar_como_admin(client, mock_auth):
    resp = client.get("/api/admin/horarios", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 4


def test_listar_filtrado_por_profesor(client, mock_auth):
    resp = client.get(
        "/api/admin/horarios?profesor_id=u-pro-001",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3
    for h in data:
        assert h["profesor_id"] == "u-pro-001"


# -------- Crear --------

def test_crear_ok(client, mock_auth):
    resp = client.post("/api/admin/horarios", json=_PAYLOAD, headers=mock_auth.as_admin())
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["profesor_id"] == "u-pro-001"
    assert data["dia_semana"] == 3
    assert data["hora_inicio"] == "14:00"
    assert data["hora_fin"] == "18:00"
    assert data["notas"] == "Turno tarde"


def test_crear_solapamiento_falla(client, mock_auth):
    payload = {**_PAYLOAD, "dia_semana": 0, "hora_inicio": "10:00", "hora_fin": "14:00"}
    resp = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "HorarioSolapado"


def test_crear_hora_invalida(client, mock_auth):
    payload = {**_PAYLOAD, "hora_inicio": "25:00"}
    resp = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


def test_crear_rango_invalido(client, mock_auth):
    payload = {**_PAYLOAD, "hora_inicio": "18:00", "hora_fin": "14:00"}
    resp = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


def test_crear_dia_invalido(client, mock_auth):
    payload = {**_PAYLOAD, "dia_semana": 9}
    resp = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


def test_crear_profesor_inexistente(client, mock_auth):
    payload = {**_PAYLOAD, "profesor_id": "u-pro-999"}
    resp = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp.status_code == 400


# -------- Editar --------

def test_editar_ok(client, mock_auth):
    resp = client.put(
        "/api/admin/horarios/hor-001",
        json={"hora_inicio": "09:00", "hora_fin": "13:00"},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["hora_inicio"] == "09:00"
    assert data["hora_fin"] == "13:00"


def test_editar_con_solapamiento_falla(client, mock_auth):
    client.put(
        "/api/admin/horarios/hor-002",
        json={"hora_inicio": "10:00", "hora_fin": "14:00"},
        headers=mock_auth.as_admin(),
    )
    payload = {
        "profesor_id": "u-pro-001",
        "dia_semana": 2,
        "hora_inicio": "12:00",
        "hora_fin": "16:00",
    }
    resp2 = client.post("/api/admin/horarios", json=payload, headers=mock_auth.as_admin())
    assert resp2.status_code == 400


def test_editar_inexistente(client, mock_auth):
    resp = client.put(
        "/api/admin/horarios/hor-999",
        json={"hora_inicio": "09:00"},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 404


def test_editar_payload_vacio(client, mock_auth):
    resp = client.put("/api/admin/horarios/hor-001", json={}, headers=mock_auth.as_admin())
    assert resp.status_code == 400


# -------- Eliminar --------

def test_eliminar_ok(client, mock_auth):
    resp = client.delete("/api/admin/horarios/hor-001", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    assert resp.get_json()["data"]["eliminado"] is True

    resp2 = client.get("/api/admin/horarios/hor-001", headers=mock_auth.as_admin())
    assert resp2.status_code == 404


def test_eliminar_inexistente(client, mock_auth):
    resp = client.delete("/api/admin/horarios/hor-999", headers=mock_auth.as_admin())
    assert resp.status_code == 404


# -------- Profesores --------

def test_listar_profesores(client, mock_auth):
    resp = client.get("/api/admin/profesores", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [p["id"] for p in data]
    assert "u-pro-001" in ids
    assert "u-gim-001" in ids


# -------- Mis horarios (profesor) --------

def test_mis_horarios(client, mock_auth):
    resp = client.get("/api/profesor/mis-horarios", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3
    for h in data:
        assert h["profesor_id"] == "u-pro-001"


def test_mis_horarios_alumno_403(client, mock_auth):
    resp = client.get("/api/profesor/mis-horarios", headers=mock_auth.as_alumno())
    assert resp.status_code == 403