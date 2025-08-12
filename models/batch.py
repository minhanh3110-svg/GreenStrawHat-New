from extensions import db
from datetime import datetime

class Batch(db.Model):
    __tablename__ = "batches"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"))
    start_date = db.Column(db.Date, default=datetime.utcnow)
    stage = db.Column(db.String(30))
    plan_formula_id = db.Column(db.Integer, db.ForeignKey("media_formulas.id"))
    current_room_id = db.Column(db.Integer, db.ForeignKey("env_rooms.id"))
    status = db.Column(db.String(20), default="ACTIVE")

class BatchOperation(db.Model):
    __tablename__ = "batch_operations"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"))
    op_type = db.Column(db.String(20))  # INOCULATION/SUBCULTURE/SPLIT/MOVE/DISCARD/HARVEST
    date = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    qty_in = db.Column(db.Integer)
    qty_out = db.Column(db.Integer)
    contamination = db.Column(db.Float)  # %
    notes = db.Column(db.Text)
