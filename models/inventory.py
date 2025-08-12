from extensions import db
from datetime import datetime

class InventoryItem(db.Model):
    __tablename__ = "inventory_items"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    uom = db.Column(db.String(20), default="unit")
    type = db.Column(db.String(32))  # chemical, consumable, container
    safety_stock = db.Column(db.Float, default=0.0)

class InventoryTx(db.Model):
    __tablename__ = "inventory_tx"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"))
    qty = db.Column(db.Float, nullable=False)
    uom = db.Column(db.String(20), default="unit")
    direction = db.Column(db.String(8))  # IN/OUT
    reason = db.Column(db.String(64))
    ref_table = db.Column(db.String(64))
    ref_id = db.Column(db.Integer)
    tx_date = db.Column(db.DateTime, default=datetime.utcnow)
