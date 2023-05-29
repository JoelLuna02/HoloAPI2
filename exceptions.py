from flask import Flask
from werkzeug.exceptions import HTTPException

def flask_exceptions(app: Flask):
    @app.errorhandler(HTTPException)
    def error500(e):
        response = {
            "error": e.name,
            "code": e.code,
            "message": e.description
        }
        return response, e.code
    
    @app.errorhandler(Exception)
    def exceptio(e):
        response = {
            "error": "Internal Service Error",
            "code": 500,
            "message": str(e)
        }
        return response, 500