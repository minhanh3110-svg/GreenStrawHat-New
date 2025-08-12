from extensions import db

class MediaFormula(db.Model):
    __tablename__ = "media_formulas"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(20), default="v1")
    composition_json = db.Column(db.Text)  # JSON string
    ph = db.Column(db.Float)
    ster_time_min = db.Column(db.Integer)
    updated_by = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
