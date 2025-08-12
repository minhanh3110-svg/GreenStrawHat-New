from .species import bp as species_bp
from .batches import bp as batches_bp

def register_api(app):
    app.register_blueprint(species_bp)
    app.register_blueprint(batches_bp)
