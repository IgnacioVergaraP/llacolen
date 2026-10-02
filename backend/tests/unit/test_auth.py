def test_login_ok_alumno(client):
    resp = client.post("/api/auth/login", json={
        "email": "alumno@gimnasio.com",
        "password": "alumno123",
    })
    assert resp.status_code == 200
    body = resp.get_json()["data"]
    assert "token" in body
    assert body["usuario"]["rol"] == "alumno"
    assert "password_hash" not in body["usuario"]


def test_login_credenciales_invalidas(client):
    resp = client.post("/api/auth/login", json={
        "email": "alumno@gimnasio.com",
        "password": "incorrecta",
    })
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"]["name"] == "InvalidCredentials"


def test_login_email_inexistente(client):
    resp = client.post("/api/auth/login", json={
        "email": "nadie@gimnasio.com",
        "password": "cualquiera",
    })
    assert resp.status_code == 401


def test_login_payload_invalido(client):
    resp = client.post("/api/auth/login", json={"email": "no-email"})
    assert resp.status_code == 400


def test_me_sin_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.get_json()["error"]["name"] == "MissingToken"


def test_me_con_token_valido(client):
    login = client.post("/api/auth/login", json={
        "email": "profesor@gimnasio.com",
        "password": "profe123",
    }).get_json()["data"]
    token = login["token"]

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["rol"] == "profesor"


def test_me_token_invalido(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer no-es-un-jwt"})
    assert resp.status_code == 401
    assert resp.get_json()["error"]["name"] == "InvalidToken"