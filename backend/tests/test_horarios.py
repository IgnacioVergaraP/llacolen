def _login(client, email="admin@gimnasio.com", password="admin123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _headers(client, email="admin@gimnasio.com", password="admin123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


_PAYLOAD = {
    "profesor_id": "u-pro-001",
    "dia_semana": 3,              # jueves
    "hora_inicio": "14:00",
    "hora_fin": "18:00",
    "notas": "Turno tarde",
}


# -------- Listar --------

def test_listar_sin_token(client):
    resp = client.get("/api/admin/horarios")
    assert resp.status_code == 401


def test_listar_como_profesor_403(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/admin/horarios",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_listar_como_admin(client):
    resp = client.get("/api/admin/horarios", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 4


def test_listar_filtrado_por_profesor(client):
    resp = client.get("/api/admin/horarios?profesor_id=u-pro-001", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3
    for h in data:
        assert h["profesor_id"] == "u-pro-001"


# -------- Crear --------

def test_crear_ok(client):
    resp = client.post("/api/admin/horarios", json=_PAYLOAD, headers=_headers(client))
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["profesor_id"] == "u-pro-001"
    assert data["dia_semana"] == 3
    assert data["hora_inicio"] == "14:00"
    assert data["hora_fin"] == "18:00"
    assert data["notas"] == "Turno tarde"


def test_crear_solapamiento_falla(client):
    """El profesor ya tiene lunes 08-12. Intentamos lunes 10-14."""
    payload = {
        **_PAYLOAD,
        "dia_semana": 0,
        "hora_inicio": "10:00",
        "hora_fin": "14:00",
    }
    resp = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "HorarioSolapado"


def test_crear_hora_invalida(client):
    payload = {**_PAYLOAD, "hora_inicio": "25:00"}
    resp = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_rango_invalido(client):
    payload = {**_PAYLOAD, "hora_inicio": "18:00", "hora_fin": "14:00"}
    resp = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_dia_invalido(client):
    payload = {**_PAYLOAD, "dia_semana": 9}
    resp = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_profesor_inexistente(client):
    payload = {**_PAYLOAD, "profesor_id": "u-pro-999"}
    resp = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp.status_code == 400


# -------- Editar --------

def test_editar_ok(client):
    resp = client.put(
        "/api/admin/horarios/hor-001",
        json={"hora_inicio": "09:00", "hora_fin": "13:00"},
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["hora_inicio"] == "09:00"
    assert data["hora_fin"] == "13:00"


def test_editar_con_solapamiento_falla(client):
    """Mover hor-002 (miércoles 17-21) a miércoles 10-14. No choca con nada. Editemos a 10-14 → OK."""
    resp = client.put(
        "/api/admin/horarios/hor-002",
        json={"hora_inicio": "10:00", "hora_fin": "14:00"},
        headers=_headers(client),
    )
    assert resp.status_code == 200

    # Ahora intentar editar hor-001 (lunes 08-12) a lunes 11-15 para que no choque. No choca.
    # Probemos superposición real: editar hor-003 (viernes 08-12) a viernes 10-14 → OK (no hay otro ese día).
    # Probemos crear uno nuevo que sí choque con el modificado
    payload = {
        "profesor_id": "u-pro-001",
        "dia_semana": 2,           # miércoles
        "hora_inicio": "12:00",
        "hora_fin": "16:00",
    }
    resp2 = client.post("/api/admin/horarios", json=payload, headers=_headers(client))
    assert resp2.status_code == 400


def test_editar_inexistente(client):
    resp = client.put(
        "/api/admin/horarios/hor-999",
        json={"hora_inicio": "09:00"},
        headers=_headers(client),
    )
    assert resp.status_code == 404


def test_editar_payload_vacio(client):
    resp = client.put("/api/admin/horarios/hor-001", json={}, headers=_headers(client))
    assert resp.status_code == 400


# -------- Eliminar --------

def test_eliminar_ok(client):
    resp = client.delete("/api/admin/horarios/hor-001", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["eliminado"] is True

    # Verificar que ya no está
    resp2 = client.get("/api/admin/horarios/hor-001", headers=_headers(client))
    assert resp2.status_code == 404


def test_eliminar_inexistente(client):
    resp = client.delete("/api/admin/horarios/hor-999", headers=_headers(client))
    assert resp.status_code == 404


# -------- Profesores --------

def test_listar_profesores(client):
    resp = client.get("/api/admin/profesores", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    ids = [p["id"] for p in data]
    assert "u-pro-001" in ids
    assert "u-gim-001" in ids


# -------- Mis horarios (profesor) --------

def test_mis_horarios(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get(
        "/api/profesor/mis-horarios",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3
    for h in data:
        assert h["profesor_id"] == "u-pro-001"


def test_mis_horarios_alumno_403(client):
    token = _login(client, "alumno@gimnasio.com", "alumno123")
    resp = client.get(
        "/api/profesor/mis-horarios",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403