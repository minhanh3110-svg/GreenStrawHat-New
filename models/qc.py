from extensions import db
from datetime import datetime

class QCCheck(db.Model):
    __tablename__ = "qc_checks"
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(32))  # batch/media
    entity_id = db.Column(db.Integer)
    check_point = db.Column(db.String(64))
    result = db.Column(db.String(32))  # PASS/FAIL
    value = db.Column(db.Float)
    unit = db.Column(db.String(16))
    checked_by = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.utcnow)
