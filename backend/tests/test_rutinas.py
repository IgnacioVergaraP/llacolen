def _login(client, email="profesor@gimnasio.com", password="profe123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["token"]


def _headers(client, email="profesor@gimnasio.com", password="profe123"):
    return {"Authorization": f"Bearer {_login(client, email, password)}"}


_PAYLOAD_RUTINA = {
    "alumno_id": "u-alu-001",
    "titulo": "Rutina de prueba",
    "grupos_musculares": ["pecho", "triceps"],
    "ejercicios": [
        {
            "tipo": "maquina",
            "maquina_id": "mq-001",
            "series": 4,
            "repeticiones": "10",
            "peso_sugerido": "60 kg",
        },
        {
            "tipo": "libre",
            "nombre": "Fondos en paralelas",
            "descripcion": "Ejercicio de empuje.",
            "series": 3,
            "repeticiones": "Al fallo",
            "peso_sugerido": "Corporal",
        },
    ],
}


# -------- Listar --------

def test_listar_sin_token(client):
    resp = client.get("/api/profesor/rutinas")
    assert resp.status_code == 401


def test_listar_como_alumno_403(client):
    token = _login(client, "alumno@gimnasio.com", "alumno123")
    resp = client.get(
        "/api/profesor/rutinas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_listar_como_profesor(client):
    resp = client.get("/api/profesor/rutinas", headers=_headers(client))
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 5
    for r in data:
        assert r["profesor_id"] == "u-pro-001"


# -------- Crear --------

def test_crear_ok(client):
    resp = client.post("/api/profesor/rutinas", json=_PAYLOAD_RUTINA, headers=_headers(client))
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["titulo"] == "Rutina de prueba"
    assert data["alumno_id"] == "u-alu-001"
    assert data["profesor_id"] == "u-pro-001"
    assert data["activa"] is True
    assert len(data["ejercicios"]) == 2
    assert data["ejercicios"][0]["maquina"]["nombre"] == "Press de banca"


def test_crear_sin_ejercicios_falla(client):
    payload = {**_PAYLOAD_RUTINA, "ejercicios": []}
    resp = client.post("/api/profesor/rutinas", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_alumno_inexistente(client):
    payload = {**_PAYLOAD_RUTINA, "alumno_id": "u-alu-999"}
    resp = client.post("/api/profesor/rutinas", json=payload, headers=_headers(client))
    assert resp.status_code == 400


def test_crear_maquina_inexistente_en_ejercicio(client):
    payload = {
        **_PAYLOAD_RUTINA,
        "ejercicios": [
            {"tipo": "maquina", "maquina_id": "mq-999", "series": 3, "repeticiones": "10"},
        ],
    }
    resp = client.post("/api/profesor/rutinas", json=payload, headers=_headers(client))
    # No valida existencia de máquina en el schema, así que se guarda igual.
    # Solo validamos que no rompe.
    assert resp.status_code == 201


# -------- Editar --------

def test_editar_ok(client):
    creada = client.post("/api/profesor/rutinas", json=_PAYLOAD_RUTINA, headers=_headers(client)).get_json()["data"]

    payload_edit = {
        "titulo": "Rutina editada",
        "grupos_musculares": ["pecho"],
        "ejercicios": [
            {"tipo": "maquina", "maquina_id": "mq-002", "series": 5, "repeticiones": "8"},
        ],
    }
    resp = client.put(
        f"/api/profesor/rutinas/{creada['id']}",
        json=payload_edit,
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["titulo"] == "Rutina editada"
    assert len(data["ejercicios"]) == 1


def test_editar_ajena_404(client):
    """El admin no puede editar rutinas del profesor Martínez."""
    resp = client.put(
        "/api/profesor/rutinas/rt-001",
        json={"titulo": "X", "grupos_musculares": [], "ejercicios": [{"tipo": "libre", "nombre": "X", "series": 1, "repeticiones": "1"}]},
        headers=_headers(client, "admin@gimnasio.com", "admin123"),
    )
    assert resp.status_code == 404


# -------- Archivar / Reactivar --------

def test_archivar_ok(client):
    creada = client.post("/api/profesor/rutinas", json=_PAYLOAD_RUTINA, headers=_headers(client)).get_json()["data"]
    resp = client.patch(f"/api/profesor/rutinas/{creada['id']}/archivar", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["activa"] is False


def test_reactivar_ok(client):
    creada = client.post("/api/profesor/rutinas", json=_PAYLOAD_RUTINA, headers=_headers(client)).get_json()["data"]
    client.patch(f"/api/profesor/rutinas/{creada['id']}/archivar", headers=_headers(client))
    resp = client.patch(f"/api/profesor/rutinas/{creada['id']}/reactivar", headers=_headers(client))
    assert resp.status_code == 200
    assert resp.get_json()["data"]["activa"] is True


# -------- Duplicar --------

def test_duplicar_ok(client):
    resp = client.post(
        "/api/profesor/rutinas/rt-001/duplicar",
        json={"nuevo_alumno_id": "u-alu-004"},
        headers=_headers(client),
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["alumno_id"] == "u-alu-004"
    assert data["titulo"] == "Rutina de espalda y bíceps"
    assert data["profesor_id"] == "u-pro-001"
    assert len(data["ejercicios"]) == 4


def test_duplicar_a_alumno_inexistente(client):
    resp = client.post(
        "/api/profesor/rutinas/rt-001/duplicar",
        json={"nuevo_alumno_id": "u-alu-999"},
        headers=_headers(client),
    )
    assert resp.status_code == 400


# -------- Rutinas de un alumno --------

def test_rutinas_de_alumno(client):
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/rutinas",
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3


def test_rutinas_de_alumno_incluir_inactivas(client):
    # Archivo rt-001 y verifico que aparece con incluir_inactivas=true
    client.patch("/api/profesor/rutinas/rt-001/archivar", headers=_headers(client))
    resp = client.get(
        "/api/profesor/alumnos/u-alu-001/rutinas?incluir_inactivas=true",
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data) == 3


# -------- Editar datos del alumno --------

def test_editar_datos_alumno(client):
    resp = client.patch(
        "/api/profesor/alumnos/u-alu-001/perfil",
        json={
            "peso_actual": 74.0,
            "porcentaje_grasa": 13.8,
            "notas_profesor": "Excelente progreso este mes.",
        },
        headers=_headers(client),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["peso_actual"] == 74.0
    assert data["porcentaje_grasa"] == 13.8
    assert data["notas_profesor"] == "Excelente progreso este mes."
    # Verificamos que se marca como medido por profesor
    assert data["origen_grasa"] == "profesor"
    assert data["cargado_por_id"] == "u-pro-001"


def test_editar_datos_alumno_inexistente(client):
    resp = client.patch(
        "/api/profesor/alumnos/u-alu-999/perfil",
        json={"peso_actual": 74.0},
        headers=_headers(client),
    )
    assert resp.status_code == 404


def test_editar_datos_alumno_no_permite_nombre(client):
    """El schema ignora campos no permitidos, así que pasar 'nombre' no lo cambia."""
    resp = client.patch(
        "/api/profesor/alumnos/u-alu-001/perfil",
        json={"nombre": "Hackeado"},
        headers=_headers(client),
    )
    # El schema no acepta "nombre" en el payload → error EmptyPayload
    assert resp.status_code == 400


# -------- Integración con solicitud de rutina --------

def test_crear_rutina_resuelve_solicitud_activa(client):
    """Si el alumno tiene una solicitud activa, se resuelve al crear la rutina."""
    # Lucía tiene srt-0002 pendiente
    payload = {**_PAYLOAD_RUTINA, "alumno_id": "u-alu-004"}
    resp = client.post("/api/profesor/rutinas", json=payload, headers=_headers(client))
    assert resp.status_code == 201
    rutina = resp.get_json()["data"]

    # Verifico que la solicitud quedó resuelta
    solicitudes = client.get(
        "/api/profesor/solicitudes-rutina/tomadas",
        headers=_headers(client),
    ).get_json()["data"]
    resueltas = [s for s in solicitudes if s["estado"] == "resuelta" and s["rutina_id"] == rutina["id"]]
    assert len(resueltas) >= 1