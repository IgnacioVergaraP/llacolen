"""
Tests del blueprint profesor: reportes de problemas.
"""


_PAYLOAD = {
    "tipo": "rota",
    "prioridad": "alta",
    "descripcion": "La máquina no enciende, no responde al botón de inicio.",
    "maquina_id": "mq-001",
    "foto_url": None,
}


# -------- Crear --------

def test_crear_sin_token(client):
    resp = client.post("/api/profesor/reportes", json=_PAYLOAD)
    assert resp.status_code == 401


def test_crear_como_alumno_403(client, mock_auth):
    resp = client.post(
        "/api/profesor/reportes",
        json=_PAYLOAD,
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 403


def test_crear_ok(client, mock_auth):
    resp = client.post("/api/profesor/reportes", json=_PAYLOAD, headers=mock_auth.as_profesor())
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["estado"] == "abierto"
    assert data["tipo"] == "rota"
    assert data["prioridad"] == "alta"
    assert data["maquina_id"] == "mq-001"
    assert data["maquina_nombre"] == "Press de banca"
    assert data["reportante_id"] == "u-pro-001"


def test_crear_sin_maquina(client, mock_auth):
    payload = {**_PAYLOAD, "maquina_id": None}
    resp = client.post("/api/profesor/reportes", json=payload, headers=mock_auth.as_profesor())
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["maquina_id"] is None
    assert data["maquina_nombre"] is None


def test_crear_maquina_inexistente(client, mock_auth):
    payload = {**_PAYLOAD, "maquina_id": "mq-999"}
    resp = client.post("/api/profesor/reportes", json=payload, headers=mock_auth.as_profesor())
    assert resp.status_code == 400


def test_crear_tipo_invalido(client, mock_auth):
    payload = {**_PAYLOAD, "tipo": "inventado"}
    resp = client.post("/api/profesor/reportes", json=payload, headers=mock_auth.as_profesor())
    assert resp.status_code == 400


def test_crear_prioridad_invalida(client, mock_auth):
    payload = {**_PAYLOAD, "prioridad": "super-urgente"}
    resp = client.post("/api/profesor/reportes", json=payload, headers=mock_auth.as_profesor())
    assert resp.status_code == 400


def test_crear_descripcion_corta(client, mock_auth):
    payload = {**_PAYLOAD, "descripcion": "corto"}
    resp = client.post("/api/profesor/reportes", json=payload, headers=mock_auth.as_profesor())
    assert resp.status_code == 400


# -------- Listar míos --------

def test_mis_reportes(client, mock_auth):
    resp = client.get("/api/profesor/reportes/mios", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 2
    for r in data:
        assert r["reportante_id"] == "u-pro-001"


# -------- Cancelar --------

def test_cancelar_abierto_ok(client, mock_auth):
    creado = client.post(
        "/api/profesor/reportes", json=_PAYLOAD, headers=mock_auth.as_profesor()
    ).get_json()["data"]
    resp = client.post(
        f"/api/profesor/reportes/{creado['id']}/cancelar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "cancelado"


def test_cancelar_resuelto_falla(client, mock_auth):
    """rep-0002 está resuelto."""
    resp = client.post(
        "/api/profesor/reportes/rep-0002/cancelar",
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 400


def test_cancelar_ajeno_404(client, mock_auth):
    resp = client.post(
        "/api/profesor/reportes/rep-0001/cancelar",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 404


# -------- Admin --------

def test_admin_count(client, mock_auth):
    resp = client.get("/api/profesor/admin/reportes/count", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "abiertos" in data
    assert "en_revision" in data
    assert "resueltos" in data
    assert "total_pendientes" in data


def test_admin_listar(client, mock_auth):
    resp = client.get("/api/profesor/admin/reportes", headers=mock_auth.as_admin())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 2


def test_admin_marcar_en_revision(client, mock_auth):
    creado = client.post(
        "/api/profesor/reportes", json=_PAYLOAD, headers=mock_auth.as_profesor()
    ).get_json()["data"]
    resp = client.post(
        f"/api/profesor/admin/reportes/{creado['id']}/en-revision",
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["estado"] == "en_revision"


def test_admin_resolver_con_nota(client, mock_auth):
    creado = client.post(
        "/api/profesor/reportes", json=_PAYLOAD, headers=mock_auth.as_profesor()
    ).get_json()["data"]
    resp = client.post(
        f"/api/profesor/admin/reportes/{creado['id']}/resolver",
        json={"resolucion": "Se reemplazó el cable dañado."},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["estado"] == "resuelto"
    assert data["resolucion"] == "Se reemplazó el cable dañado."
    assert data["revisado_por_nombre"] == "Admin Gimnasio"


def test_admin_resolver_sin_nota(client, mock_auth):
    creado = client.post(
        "/api/profesor/reportes", json=_PAYLOAD, headers=mock_auth.as_profesor()
    ).get_json()["data"]
    resp = client.post(
        f"/api/profesor/admin/reportes/{creado['id']}/resolver",
        json={},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["resolucion"] is None


def test_admin_resolver_ya_resuelto_falla(client, mock_auth):
    resp = client.post(
        "/api/profesor/admin/reportes/rep-0002/resolver",
        json={},
        headers=mock_auth.as_admin(),
    )
    assert resp.status_code == 400