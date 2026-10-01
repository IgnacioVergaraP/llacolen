from flask import jsonify


def ok(data=None, status: int = 200):
    """Respuesta exitosa estándar."""
    payload = {"data": data} if data is not None else {"data": None}
    return jsonify(payload), status


def created(data=None):
    return ok(data, status=201)


def error(message: str, code: int = 400, name: str = "BadRequest"):
    """Respuesta de error estándar (mismo shape que errors.py)."""
    return jsonify({
        "error": {"code": code, "name": name, "message": message}
    }), code