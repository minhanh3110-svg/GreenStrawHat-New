from extensions import db

class EnvRoom(db.Model):
    __tablename__ = "env_rooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(32))  # inoculation, growth, media
    capacity = db.Column(db.Integer)
    temp_set = db.Column(db.Float)
    light_set = db.Column(db.Float)
    humidity_set = db.Column(db.Float)

class Shelf(db.Model):
    __tablename__ = "shelves"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("env_rooms.id"))
    name = db.Column(db.String(64))
    rows = db.Column(db.Integer, default=4)
    cols = db.Column(db.Integer, default=8)

class Tray(db.Model):
    __tablename__ = "trays"
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey("shelves.id"))
    code = db.Column(db.String(64), unique=True)
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)
    capacity = db.Column(db.Integer, default=100)
    status = db.Column(db.String(32), default="AVAILABLE")
