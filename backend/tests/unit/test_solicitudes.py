"""
Tests del blueprint profesor: solicitudes de ejercicios.
"""


_PAYLOAD_VALIDO = {
    "nombre": "Máquina de prueba",
    "grupos_musculares": ["pecho", "triceps"],
    "descripcion": "Descripción de prueba suficientemente larga.",
    "video_url": "https://www.youtube.com/embed/abc",
    "imagen_url": "",
}


# -------- Crear --------

def test_crear_sin_token(client):
    resp = client.post("/api/profesor/solicitudes", json=_PAYLOAD_VALIDO)
    assert resp.status_code == 401


def test_crear_como_alumno_403(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 403


def test_crear_ok(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["estado"] == "pendiente"
    assert data["nombre"] == _PAYLOAD_VALIDO["nombre"]
    assert data["solicitante_id"] == "u-pro-001"


def test_crear_payload_invalido(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes",
        json={"nombre": "X"},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


def test_crear_sin_grupos(client, mock_auth):
    payload = dict(_PAYLOAD_VALIDO)
    payload["grupos_musculares"] = []
    resp = client.post(
        "/api/profesor/solicitudes",
        json=payload,
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


def test_crear_url_invalida(client, mock_auth):
    payload = dict(_PAYLOAD_VALIDO)
    payload["video_url"] = "no-es-url"
    resp = client.post(
        "/api/profesor/solicitudes",
        json=payload,
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


# -------- Listar mías --------

def test_mis_solicitudes(client, mock_auth):
    resp = client.get("/api/profesor/solicitudes/mias", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    for s in data:
        assert s["solicitante_id"] == "u-pro-001"


# -------- Cancelar --------

def test_cancelar_ok(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    resp = client.post(
        f"/api/profesor/solicitudes/{creada['id']}/cancelar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "cancelada"


def test_cancelar_ajena_404(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    resp = client.post(
        f"/api/profesor/solicitudes/{creada['id']}/cancelar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 404


# -------- Admin --------

def test_admin_count_pendientes(client, mock_auth):
    resp = client.get("/api/profesor/admin/pendientes/count", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "count" in data
    assert data["count"] >= 1


def test_admin_count_como_profesor_403(client, mock_auth):
    resp = client.get("/api/profesor/admin/pendientes/count", headers=mock_auth.as_profesor())
    assert resp.status_code == 403


def test_admin_listar_pendientes(client, mock_auth):
    resp = client.get("/api/profesor/admin/pendientes", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    for s in data:
        assert s["estado"] == "pendiente"


def test_admin_aprobar(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    resp = client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/aprobar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "aprobada"
    assert data["maquina_id_creado"] is not None
    assert data["maquina_id_creado"].startswith("mq-")


def test_admin_rechazar(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    resp = client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/rechazar",
        json={"motivo": "Falta información sobre la máquina."},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "rechazada"
    assert data["motivo_rechazo"] == "Falta información sobre la máquina."


def test_admin_rechazar_sin_motivo(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    resp = client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/rechazar",
        json={},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 400


def test_admin_aprobar_dos_veces_falla(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/aprobar",
        headers=mock_auth.as_admin(),
    )
    resp = client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/aprobar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 400


def test_admin_aprobar_crea_maquina_en_catalogo(client, mock_auth):
    creada = client.post(
        "/api/profesor/solicitudes",
        json=_PAYLOAD_VALIDO,
        headers=mock_auth.as_profesor(),
    ).get_json()["data"]

    aprobada = client.post(
        f"/api/profesor/admin/solicitudes/{creada['id']}/aprobar",
        headers=mock_auth.as_admin(),
    ).get_json()["data"]

    maquina_id = aprobada["maquina_id_creado"]
    resp = client.get(f"/api/maquinas/{maquina_id}", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    assert resp.get_json()["data"]["nombre"] == _PAYLOAD_VALIDO["nombre"]