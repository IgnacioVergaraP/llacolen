from flask import jsonify
from werkzeug.exceptions import HTTPException


class AuthError(Exception):
    """Error de autenticación/autorización.

    code: HTTP status code
    name: identificador legible (InvalidCredentials, TokenExpired, ...)
    message: mensaje para el cliente
    """
    def __init__(self, code: int, name: str, message: str):
        super().__init__(message)
        self.code = code
        self.name = name
        self.message = message


def register_error_handlers(app):
    @app.errorhandler(AuthError)
    def handle_auth_error(e: AuthError):
        return jsonify({
            "error": {
                "code": e.code,
                "name": e.name,
                "message": e.message,
            }
        }), e.code

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return jsonify({
            "error": {
                "code": e.code,
                "name": e.name,
                "message": e.description,
            }
        }), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception):
        app.logger.exception("Error inesperado")
        return jsonify({
            "error": {
                "code": 500,
                "name": "InternalServerError",
                "message": "Ocurrió un error inesperado.",
            }
        }), 500