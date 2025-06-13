from .auth import auth_bp
from .deaths import deaths_bp
from .unemployment import unemployment_bp
from .export import export_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(deaths_bp, url_prefix="/api/v1/deaths")
    app.register_blueprint(unemployment_bp, url_prefix="/api/v1/unemployment")
    app.register_blueprint(export_bp, url_prefix="/api/v1")
