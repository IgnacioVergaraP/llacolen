"""
Tests del blueprint profesor: solicitudes de rutina.
"""


_PAYLOAD_ALUMNO = {
    "objetivo": "hipertrofia",
    "dias_por_semana": 4,
    "comentarios": "Quiero enfocarme en tren superior.",
    "grupos_interes": ["pecho", "espalda"],
    "profesor_preferido_id": None,
}


# -------- Crear (alumno) --------

def test_crear_sin_token(client):
    resp = client.post("/api/profesor/solicitudes-rutina", json=_PAYLOAD_ALUMNO)
    assert resp.status_code == 401


def test_crear_ok(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=_PAYLOAD_ALUMNO,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["estado"] == "pendiente"
    assert data["alumno_id"] == "u-alu-001"
    assert data["objetivo"] == "hipertrofia"
    assert data["dias_por_semana"] == 4


def test_crear_con_profesor_preferido(client, mock_auth):
    payload = {**_PAYLOAD_ALUMNO, "profesor_preferido_id": "u-pro-001"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["profesor_preferido_id"] == "u-pro-001"
    assert data["profesor_preferido_nombre"] == "Prof. Martínez"


def test_crear_profesor_inexistente(client, mock_auth):
    payload = {**_PAYLOAD_ALUMNO, "profesor_preferido_id": "u-pro-999"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_crear_objetivo_invalido(client, mock_auth):
    payload = {**_PAYLOAD_ALUMNO, "objetivo": "inventado"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_crear_dias_invalidos(client, mock_auth):
    payload = {**_PAYLOAD_ALUMNO, "dias_por_semana": 0}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_crear_duplicada_falla(client, mock_auth):
    """María ya tiene una solicitud pendiente (srt-0001)."""
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=_PAYLOAD_ALUMNO,
        headers=mock_auth.as_user("u-alu-002"),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "SolicitudActiva"


# -------- Listar (alumno) --------

def test_mis_solicitudes(client, mock_auth):
    resp = client.get(
        "/api/profesor/solicitudes-rutina/mias",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)


def test_mis_solicitudes_maria(client, mock_auth):
    resp = client.get(
        "/api/profesor/solicitudes-rutina/mias",
        headers=mock_auth.as_user("u-alu-002"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) >= 1
    for s in data:
        assert s["alumno_id"] == "u-alu-002"


# -------- Cancelar (alumno) --------

def test_cancelar_propia(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/cancelar",
        headers=mock_auth.as_user("u-alu-004"),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "cancelada"


def test_cancelar_ajena_404(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/cancelar",
        headers=mock_auth.as_user("u-alu-004"),
    )
    assert resp.status_code == 404


# -------- Disponibles (profesor) --------

def test_disponibles_profesor_martinez(client, mock_auth):
    resp = client.get(
        "/api/profesor/solicitudes-rutina/disponibles",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    assert "srt-0001" in ids
    assert "srt-0002" in ids


def test_disponibles_otro_profesor(client, mock_auth):
    resp = client.get(
        "/api/profesor/solicitudes-rutina/disponibles",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    assert "srt-0002" in ids
    assert "srt-0001" not in ids


# -------- Tomar --------

def test_tomar_pool(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "en_proceso"
    assert data["profesor_id"] == "u-pro-001"


def test_tomar_dirigida_a_mi(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/tomar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200


def test_tomar_dirigida_a_otro_403(client, mock_auth):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/tomar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 403


def test_tomar_ya_tomada_falla(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


# -------- Resolver / Rechazar --------

def test_resolver(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/resolver",
        json={"mensaje_resolucion": "Quedamos el jueves 19hs en recepción para armarla."},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "resuelta"
    assert "jueves" in data["mensaje_resolucion"]


def test_resolver_sin_mensaje_falla(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/resolver",
        json={},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


def test_rechazar(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/rechazar",
        json={"motivo": "No puedo tomar alumnos nuevos esta semana."},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "rechazada"


# -------- Liberación --------

def test_solicitar_liberacion(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado_liberacion"] == "solicitada"


def test_admin_ve_liberaciones_pendientes(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=mock_auth.as_profesor(),
    )
    resp = client.get(
        "/api/profesor/admin/solicitudes-rutina/liberaciones",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    assert "srt-0002" in ids


def test_admin_aprobar_liberacion(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/admin/solicitudes-rutina/srt-0002/liberar/aprobar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "pendiente"
    assert data["profesor_id"] is None
    assert data["estado_liberacion"] == "aprobada"


def test_admin_rechazar_liberacion(client, mock_auth):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=mock_auth.as_profesor(),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=mock_auth.as_profesor(),
    )
    resp = client.post(
        "/api/profesor/admin/solicitudes-rutina/srt-0002/liberar/rechazar",
        json={"motivo": "Terminá esta primera, después te libero."},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "en_proceso"
    assert data["estado_liberacion"] == "rechazada"


# -------- Profesores disponibles --------

def test_listar_profesores_disponibles(client, mock_auth):
    resp = client.get(
        "/api/profesor/profesores-disponibles",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [p["id"] for p in data]
    assert "u-pro-001" in ids
    assert "u-gim-001" in ids


# -------- Solicitudes de alumno (profesor) --------

def test_solicitudes_de_alumno_como_profesor(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-002/solicitudes-rutina",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    for s in data:
        assert s["alumno_id"] == "u-alu-002"


def test_solicitudes_de_alumno_inexistente(client, mock_auth):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-999/solicitudes-rutina",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 404