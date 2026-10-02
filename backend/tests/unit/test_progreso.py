"""
Tests del blueprint progreso.
"""
from datetime import datetime


def _hoy_iso():
    return datetime.now().strftime("%Y-%m-%d")


# ---------------- Historial ----------------

def test_historial_sin_token(client):
    resp = client.get("/api/progreso")
    assert resp.status_code == 401


def test_historial_como_alumno(client, mock_auth):
    resp = client.get("/api/progreso", headers=mock_auth.as_alumno())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    fila = data[0]
    assert {"ejercicio", "ejercicio_tipo", "fecha", "cantidad_series"} <= set(fila.keys())


def test_historial_ordenado_descendente(client, mock_auth):
    resp = client.get("/api/progreso", headers=mock_auth.as_alumno())
    data = resp.get_json()["data"]
    fechas = [f["fecha"] for f in data]
    assert fechas == sorted(fechas, reverse=True)


# ---------------- Evolución ----------------

def test_evolucion_maquina(client, mock_auth):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-001",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert isinstance(data["puntos"], list)
    assert len(data["puntos"]) >= 3


def test_evolucion_incluye_pr_historico(client, mock_auth):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-001",
        headers=mock_auth.as_alumno(),
    )
    data = resp.get_json()["data"]
    assert "pr_historico" in data
    assert data["pr_historico"] == 60.0


def test_evolucion_ejercicio_libre(client, mock_auth):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=Face pull con banda elástica",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["nombre_libre"] == "Face pull con banda elástica"


def test_evolucion_sin_datos(client, mock_auth):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-999",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["puntos"] == []
    assert data["pr_historico"] is None


# ---------------- Sesión ----------------

def test_sesion_hoy_press_banca(client, mock_auth):
    resp = client.get(
        f"/api/progreso/sesion?ejercicio=mq-001&fecha={_hoy_iso()}",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert len(data["series"]) == 3
    nums = [s["numero_serie"] for s in data["series"]]
    assert nums == sorted(nums)


def test_sesion_ejercicio_libre(client, mock_auth):
    from datetime import timedelta
    fecha = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    resp = client.get(
        f"/api/progreso/sesion?ejercicio=Face pull con banda elástica&fecha={fecha}",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["series"]) == 2


def test_sesion_sin_datos_404(client, mock_auth):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001&fecha=2000-01-01",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 404


def test_sesion_fecha_invalida(client, mock_auth):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001&fecha=hoy",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_sesion_sin_fecha(client, mock_auth):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001",
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


# ---------------- Crear ----------------

def test_crear_serie_maquina(client, mock_auth):
    resp = client.post(
        "/api/progreso",
        json={
            "ejercicio_tipo": "maquina",
            "maquina_id": "mq-001",
            "peso": "62.5 kg",
            "repeticiones": "8",
        },
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["id"].startswith("rs-")
    assert data["maquina_id"] == "mq-001"
    assert data["peso"] == "62.5 kg"
    assert data["numero_serie"] >= 1


def test_crear_serie_libre(client, mock_auth):
    resp = client.post(
        "/api/progreso",
        json={
            "ejercicio_tipo": "libre",
            "nombre_libre": "Sentadilla búlgara",
            "peso": "20 kg",
            "repeticiones": "10",
            "rutina_id": None,
        },
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["nombre_libre"] == "Sentadilla búlgara"
    assert data["maquina_id"] is None


def test_crear_serie_payload_invalido(client, mock_auth):
    resp = client.post(
        "/api/progreso",
        json={"ejercicio_tipo": "maquina"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_crear_serie_tipo_invalido(client, mock_auth):
    resp = client.post(
        "/api/progreso",
        json={"ejercicio_tipo": "otro", "peso": "10 kg", "repeticiones": "10"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_profesor_no_tiene_historial(client, mock_auth):
    resp = client.get("/api/progreso", headers=mock_auth.as_profesor())
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


# ---------------- Actualizar ----------------

def test_actualizar_serie_ok(client, mock_auth):
    headers = mock_auth.as_alumno()
    creada = client.post(
        "/api/progreso",
        json={
            "ejercicio_tipo": "maquina",
            "maquina_id": "mq-002",
            "peso": "20 kg",
            "repeticiones": "10",
        },
        headers=headers,
    ).get_json()["data"]
    rid = creada["id"]

    resp = client.patch(
        f"/api/progreso/{rid}",
        json={"peso": "22.5 kg", "repeticiones": "8"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == rid
    assert data["peso"] == "22.5 kg"
    assert data["repeticiones"] == "8"


def test_actualizar_serie_inexistente(client, mock_auth):
    resp = client.patch(
        "/api/progreso/rs-9999",
        json={"peso": "10 kg", "repeticiones": "10"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 404


def test_actualizar_serie_payload_invalido(client, mock_auth):
    resp = client.patch(
        "/api/progreso/rs-0001",
        json={"peso": "10 kg"},
        headers=mock_auth.as_alumno(),
    )
    assert resp.status_code == 400


def test_actualizar_serie_ajena_404(client, mock_auth):
    resp = client.patch(
        "/api/progreso/rs-0001",
        json={"peso": "10 kg", "repeticiones": "10"},
        headers=mock_auth.as_profesor(),
    )
    assert resp.status_code == 404