def _login(client, email="alumno@gimnasio.com", password="alumno123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _headers(client, email="alumno@gimnasio.com", password="alumno123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


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


def test_crear_ok(client):
    """Juan no tiene solicitudes activas todavía."""
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=_PAYLOAD_ALUMNO,
        headers=_headers(client),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["estado"] == "pendiente"
    assert data["alumno_id"] == "u-alu-001"
    assert data["objetivo"] == "hipertrofia"
    assert data["dias_por_semana"] == 4


def test_crear_con_profesor_preferido(client):
    payload = {**_PAYLOAD_ALUMNO, "profesor_preferido_id": "u-pro-001"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=_headers(client),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["profesor_preferido_id"] == "u-pro-001"
    assert data["profesor_preferido_nombre"] == "Prof. Martínez"


def test_crear_profesor_inexistente(client):
    payload = {**_PAYLOAD_ALUMNO, "profesor_preferido_id": "u-pro-999"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=_headers(client),
    )
    assert resp.status_code == 400


def test_crear_objetivo_invalido(client):
    payload = {**_PAYLOAD_ALUMNO, "objetivo": "inventado"}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=_headers(client),
    )
    assert resp.status_code == 400


def test_crear_dias_invalidos(client):
    payload = {**_PAYLOAD_ALUMNO, "dias_por_semana": 0}
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=payload,
        headers=_headers(client),
    )
    assert resp.status_code == 400


def test_crear_duplicada_falla(client):
    """María ya tiene una solicitud pendiente (srt-0001) → no puede crear otra."""
    resp = client.post(
        "/api/profesor/solicitudes-rutina",
        json=_PAYLOAD_ALUMNO,
        headers=_headers(client, "maria.gonzalez@gimnasio.com", "maria123"),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"]["name"] == "SolicitudActiva"


# -------- Listar (alumno) --------

def test_mis_solicitudes(client):
    resp = client.get("/api/profesor/solicitudes-rutina/mias", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)


def test_mis_solicitudes_maria(client):
    resp = client.get(
        "/api/profesor/solicitudes-rutina/mias",
        headers=_headers(client, "maria.gonzalez@gimnasio.com", "maria123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) >= 1
    for s in data:
        assert s["alumno_id"] == "u-alu-002"


# -------- Cancelar (alumno) --------

def test_cancelar_propia(client):
    """Lucía cancela su solicitud pendiente (srt-0002)."""
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/cancelar",
        headers=_headers(client, "lucia.fernandez@gimnasio.com", "lucia123"),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "cancelada"


def test_cancelar_ajena_404(client):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/cancelar",
        headers=_headers(client, "lucia.fernandez@gimnasio.com", "lucia123"),
    )
    assert resp.status_code == 404


# -------- Disponibles (profesor) --------

def test_disponibles_profesor_martinez(client):
    """El Prof. Martínez ve las del pool + las dirigidas a él."""
    resp = client.get(
        "/api/profesor/solicitudes-rutina/disponibles",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    # srt-0001 (dirigida a él) y srt-0002 (pool) deberían estar
    assert "srt-0001" in ids
    assert "srt-0002" in ids


def test_disponibles_otro_profesor(client):
    """Un profesor distinto solo ve las del pool, no las dirigidas a Martínez."""
    # Creamos un segundo profesor en el mock... o probamos que si no coincide el id, no aparece
    # Como solo hay un profesor en el mock, validamos que srt-0001 (dirigida a Martínez)
    # está en la lista de Martínez y NO debería estarlo en la de otro.
    # Por simplicidad, validamos el comportamiento desde el lado del admin que también puede tomar.
    resp = client.get(
        "/api/profesor/solicitudes-rutina/disponibles",
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    # srt-0002 (pool) sí debería estar; srt-0001 (dirigida a Martínez) NO debería
    assert "srt-0002" in ids
    assert "srt-0001" not in ids


# -------- Tomar --------

def test_tomar_pool(client):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "en_proceso"
    assert data["profesor_id"] == "u-pro-001"


def test_tomar_dirigida_a_mi(client):
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200


def test_tomar_dirigida_a_otro_403(client):
    """El admin no puede tomar una solicitud dirigida específicamente a Martínez."""
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0001/tomar",
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 403


def test_tomar_ya_tomada_falla(client):
    """Tomar srt-0002 dos veces."""
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 400


# -------- Resolver / Rechazar --------

def test_resolver(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/resolver",
        json={"mensaje_resolucion": "Quedamos el jueves 19hs en recepción para armarla."},
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "resuelta"
    assert "jueves" in data["mensaje_resolucion"]


def test_resolver_sin_mensaje_falla(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/resolver",
        json={},
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 400


def test_rechazar(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/rechazar",
        json={"motivo": "No puedo tomar alumnos nuevos esta semana."},
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "rechazada"


# -------- Liberación --------

def test_solicitar_liberacion(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado_liberacion"] == "solicitada"


def test_admin_ve_liberaciones_pendientes(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.get(
        "/api/profesor/admin/solicitudes-rutina/liberaciones",
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    ids = [s["id"] for s in data]
    assert "srt-0002" in ids


def test_admin_aprobar_liberacion(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/admin/solicitudes-rutina/srt-0002/liberar/aprobar",
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "pendiente"
    assert data["profesor_id"] is None
    assert data["estado_liberacion"] == "aprobada"


def test_admin_rechazar_liberacion(client):
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/tomar",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    client.post(
        "/api/profesor/solicitudes-rutina/srt-0002/solicitar-liberacion",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    resp = client.post(
        "/api/profesor/admin/solicitudes-rutina/srt-0002/liberar/rechazar",
        json={"motivo": "Terminá esta primera, después te libero."},
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "en_proceso"  # sigue en proceso
    assert data["estado_liberacion"] == "rechazada"

def test_listar_profesores_disponibles(client):
    resp = client.get("/api/profesor/profesores-disponibles", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    # El mock tiene 1 profesor + 1 admin del gimnasio = 2
    ids = [p["id"] for p in data]
    assert "u-pro-001" in ids
    assert "u-gim-001" in ids
    

def test_solicitudes_de_alumno_como_profesor(client):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-002/solicitudes-rutina",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    for s in data:
        assert s["alumno_id"] == "u-alu-002"


def test_solicitudes_de_alumno_inexistente(client):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-999/solicitudes-rutina",
        headers=_headers(client, "profesor@gimnasio.com", "profe123"),
    )
    assert resp.status_code == 404