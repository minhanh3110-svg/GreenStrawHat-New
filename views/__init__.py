from .auth import bp as auth_bp
from .main import bp as main_bp
from .cay_log import bp as caylog_bp

def register_views(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(caylog_bp)
