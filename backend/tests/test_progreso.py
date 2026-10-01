from datetime import datetime


def _login(client, email="alumno@gimnasio.com", password="alumno123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _auth_headers(client):
    return {"Authorization": f"Bearer {_login(client)}"}


def _hoy_iso():
    return datetime.now().strftime("%Y-%m-%d")


# ---------------- Historial ----------------

def test_historial_sin_token(client):
    resp = client.get("/api/progreso")
    assert resp.status_code == 401


def test_historial_como_alumno(client):
    resp = client.get("/api/progreso", headers=_auth_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    fila = data[0]
    assert {"ejercicio", "ejercicio_tipo", "fecha", "cantidad_series"} <= set(fila.keys())


def test_historial_ordenado_descendente(client):
    resp = client.get("/api/progreso", headers=_auth_headers(client))
    data = resp.get_json()["data"]
    fechas = [f["fecha"] for f in data]
    assert fechas == sorted(fechas, reverse=True)


# ---------------- Evolución ----------------

def test_evolucion_maquina(client):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-001",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert isinstance(data["puntos"], list)
    assert len(data["puntos"]) >= 3
    
def test_evolucion_incluye_pr_historico(client):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-001",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "pr_historico" in data
    # Press de banca tiene pesos hasta 60 kg en el mock
    assert data["pr_historico"] == 60.0


def test_evolucion_sin_datos_pr_null(client):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-999",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["pr_historico"] is None


def test_evolucion_ejercicio_libre(client):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=Face pull con banda elástica",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["nombre_libre"] == "Face pull con banda elástica"


def test_evolucion_sin_datos(client):
    resp = client.get(
        "/api/progreso/evolucion?ejercicio=mq-999",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["puntos"] == []


# ---------------- Sesión ----------------

def test_sesion_hoy_press_banca(client):
    """Hoy hay 3 series de press de banca en el mock."""
    resp = client.get(
        f"/api/progreso/sesion?ejercicio=mq-001&fecha={_hoy_iso()}",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["maquina_id"] == "mq-001"
    assert len(data["series"]) == 3
    # Ordenadas por numero_serie
    nums = [s["numero_serie"] for s in data["series"]]
    assert nums == sorted(nums)


def test_sesion_ejercicio_libre(client):
    """Face pull se registró 4 días atrás."""
    from datetime import timedelta
    fecha = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
    resp = client.get(
        f"/api/progreso/sesion?ejercicio=Face pull con banda elástica&fecha={fecha}",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["series"]) == 2


def test_sesion_sin_datos_404(client):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001&fecha=2000-01-01",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 404


def test_sesion_fecha_invalida(client):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001&fecha=hoy",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_sesion_sin_fecha(client):
    resp = client.get(
        "/api/progreso/sesion?ejercicio=mq-001",
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


# ---------------- Crear ----------------

def test_crear_serie_maquina(client):
    resp = client.post(
        "/api/progreso",
        json={
            "ejercicio_tipo": "maquina",
            "maquina_id": "mq-001",
            "peso": "62.5 kg",
            "repeticiones": "8",
        },
        headers=_auth_headers(client),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["id"].startswith("rs-")
    assert data["maquina_id"] == "mq-001"
    assert data["peso"] == "62.5 kg"
    assert data["numero_serie"] >= 1


def test_crear_serie_libre(client):
    resp = client.post(
        "/api/progreso",
        json={
            "ejercicio_tipo": "libre",
            "nombre_libre": "Sentadilla búlgara",
            "peso": "20 kg",
            "repeticiones": "10",
            "rutina_id": None,
        },
        headers=_auth_headers(client),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["nombre_libre"] == "Sentadilla búlgara"
    assert data["maquina_id"] is None


def test_crear_serie_payload_invalido(client):
    resp = client.post(
        "/api/progreso",
        json={"ejercicio_tipo": "maquina"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_crear_serie_tipo_invalido(client):
    resp = client.post(
        "/api/progreso",
        json={"ejercicio_tipo": "otro", "peso": "10 kg", "repeticiones": "10"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_profesor_no_tiene_historial(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.get("/api/progreso", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"] == []


# ---------------- Actualizar ----------------

def test_actualizar_serie_ok(client):
    headers = _auth_headers(client)
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


def test_actualizar_serie_inexistente(client):
    resp = client.patch(
        "/api/progreso/rs-9999",
        json={"peso": "10 kg", "repeticiones": "10"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 404


def test_actualizar_serie_payload_invalido(client):
    resp = client.patch(
        "/api/progreso/rs-0001",
        json={"peso": "10 kg"},
        headers=_auth_headers(client),
    )
    assert resp.status_code == 400


def test_actualizar_serie_ajena_404(client):
    token = _login(client, "profesor@gimnasio.com", "profe123")
    resp = client.patch(
        "/api/progreso/rs-0001",
        json={"peso": "10 kg", "repeticiones": "10"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404