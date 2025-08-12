from extensions import db

class Species(db.Model):
    __tablename__ = "species"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name_vi = db.Column(db.String(120), nullable=False)
    name_en = db.Column(db.String(120))
    cultivar = db.Column(db.String(120))
    notes = db.Column(db.Text)
