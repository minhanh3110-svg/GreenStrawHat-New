from flask import Blueprint, jsonify, request, send_file
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db
from models import User, Species, MediaFormula, EnvRoom, Shelf, Tray, Batch, BatchOperation, InventoryItem, InventoryTx, QCCheck
from datetime import datetime
import pandas as pd
from io import BytesIO

# AUTH
auth_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")

@auth_bp.post("/login")
def api_login():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")
    u = User.query.filter_by(username=username).first()
    if u and u.check_password(password):
        login_user(u, remember=True)
        return jsonify({"ok": True, "user": {"id": u.id, "username": u.username, "role": u.role}})
    return jsonify({"ok": False, "error": "INVALID_CREDENTIALS"}), 401

@auth_bp.post("/logout")
@login_required
def api_logout():
    logout_user()
    return jsonify({"ok": True})

@auth_bp.get("/me")
def api_me():
    if current_user.is_authenticated:
        u = current_user
        return jsonify({"authenticated": True, "user": {"id": u.id, "username": u.username, "role": u.role}})
    return jsonify({"authenticated": False})

# SPECIES
species_bp = Blueprint("species_api", __name__, url_prefix="/api/species")

@species_bp.get("")
def list_species():
    rows = Species.query.order_by(Species.id.desc()).all()
    return jsonify([{ "id": s.id, "code": s.code, "name_vi": s.name_vi, "name_en": s.name_en, "cultivar": s.cultivar } for s in rows])

@species_bp.post("")
@login_required
def create_species():
    d = request.get_json(force=True)
    s = Species(code=d["code"], name_vi=d["name_vi"], name_en=d.get("name_en"), cultivar=d.get("cultivar"))
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id}), 201

# MEDIA
media_bp = Blueprint("media_api", __name__, url_prefix="/api/media")

@media_bp.get("")
def list_media():
    rows = MediaFormula.query.order_by(MediaFormula.id.desc()).all()
    return jsonify([{ "id": m.id, "code": m.code, "name": m.name, "version": m.version, "ph": m.ph, "ster_time_min": m.ster_time_min, "is_active": m.is_active } for m in rows])

@media_bp.post("")
@login_required
def create_media():
    d = request.get_json(force=True)
    m = MediaFormula(code=d["code"], name=d["name"], version=d.get("version","v1"), composition_json=d.get("composition_json"), ph=d.get("ph"), ster_time_min=d.get("ster_time_min"), updated_by=current_user.username if current_user.is_authenticated else None)
    db.session.add(m)
    db.session.commit()
    return jsonify({"id": m.id}), 201

# BATCHES
batches_bp = Blueprint("batches_api", __name__, url_prefix="/api/batches")

@batches_bp.get("")
def list_batches():
    rows = Batch.query.order_by(Batch.id.desc()).limit(200).all()
    return jsonify([{ "id": b.id, "code": b.code, "stage": b.stage, "status": b.status } for b in rows])

@batches_bp.post("")
@login_required
def create_batch():
    d = request.get_json(force=True)
    b = Batch(code=d["code"], species_id=d["species_id"], stage=d.get("stage"), plan_formula_id=d.get("plan_formula_id"), current_room_id=d.get("current_room_id"))
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id, "code": b.code}), 201

@batches_bp.post("/<int:bid>/ops")
@login_required
def create_op(bid):
    d = request.get_json(force=True)
    op = BatchOperation(batch_id=bid, op_type=d["op_type"], qty_in=d.get("qty_in"), qty_out=d.get("qty_out"), contamination=d.get("contamination"), notes=d.get("notes"))
    db.session.add(op)
    db.session.commit()
    return jsonify({"id": op.id}), 201

# LAYOUT
layout_bp = Blueprint("layout_api", __name__, url_prefix="/api/layout")

@layout_bp.get("/rooms")
def list_rooms():
    rows = EnvRoom.query.order_by(EnvRoom.id).all()
    return jsonify([{ "id": r.id, "name": r.name, "type": r.type, "capacity": r.capacity, "temp": r.temp_set, "light": r.light_set, "humidity": r.humidity_set } for r in rows])

@layout_bp.get("/shelves")
def list_shelves():
    room_id = request.args.get("room_id", type=int)
    q = Shelf.query
    if room_id:
        q = q.filter_by(room_id=room_id)
    rows = q.order_by(Shelf.id).all()
    return jsonify([{ "id": s.id, "room_id": s.room_id, "name": s.name, "rows": s.rows, "cols": s.cols } for s in rows])

@layout_bp.get("/trays")
def list_trays():
    shelf_id = request.args.get("shelf_id", type=int)
    q = Tray.query
    if shelf_id:
        q = q.filter_by(shelf_id=shelf_id)
    rows = q.order_by(Tray.id).all()
    return jsonify([{ "id": t.id, "shelf_id": t.shelf_id, "code": t.code, "row": t.row, "col": t.col, "capacity": t.capacity, "status": t.status } for t in rows])

# INVENTORY
inventory_bp = Blueprint("inventory_api", __name__, url_prefix="/api/inventory")

@inventory_bp.get("/items")
def list_items():
    rows = InventoryItem.query.order_by(InventoryItem.id.desc()).all()
    return jsonify([{ "id": i.id, "sku": i.sku, "name": i.name, "uom": i.uom, "type": i.type, "safety_stock": i.safety_stock } for i in rows])

@inventory_bp.post("/items")
@login_required
def create_item():
    d = request.get_json(force=True)
    i = InventoryItem(sku=d["sku"], name=d["name"], uom=d.get("uom","unit"), type=d.get("type"), safety_stock=d.get("safety_stock", 0))
    db.session.add(i)
    db.session.commit()
    return jsonify({"id": i.id}), 201

@inventory_bp.post("/tx")
@login_required
def create_tx():
    d = request.get_json(force=True)
    tx = InventoryTx(item_id=d["item_id"], qty=d["qty"], uom=d.get("uom","unit"), direction=d["direction"], reason=d.get("reason"), ref_table=d.get("ref_table"), ref_id=d.get("ref_id"))
    db.session.add(tx)
    db.session.commit()
    return jsonify({"id": tx.id}), 201

# QC
qc_bp = Blueprint("qc_api", __name__, url_prefix="/api/qc")

@qc_bp.post("/checks")
@login_required
def create_qc():
    d = request.get_json(force=True)
    qc = QCCheck(entity_type=d["entity_type"], entity_id=d["entity_id"], check_point=d["check_point"], result=d.get("result","PASS"), value=d.get("value"), unit=d.get("unit"), checked_by=d.get("checked_by"))
    db.session.add(qc)
    db.session.commit()
    return jsonify({"id": qc.id}), 201

@qc_bp.get("/checks")
def list_qc():
    et = request.args.get("entity_type")
    eid = request.args.get("id", type=int)
    q = QCCheck.query
    if et: q = q.filter_by(entity_type=et)
    if eid: q = q.filter_by(entity_id=eid)
    rows = q.order_by(QCCheck.id.desc()).all()
    return jsonify([{ "id": x.id, "entity_type": x.entity_type, "entity_id": x.entity_id, "check_point": x.check_point, "result": x.result, "value": x.value, "unit": x.unit, "date": x.date.isoformat() } for x in rows])

# REPORTS
reports_bp = Blueprint("reports_api", __name__, url_prefix="/api/reports")

@reports_bp.get("")
def list_reports():
    return jsonify({"available": ["/api/reports/export?type=production"]})

@reports_bp.post("/export")
@login_required
def export_report():
    ops = BatchOperation.query.all()
    data = [{
        "batch_id": o.batch_id,
        "op_type": o.op_type,
        "date": o.date.strftime("%Y-%m-%d"),
        "qty_in": o.qty_in,
        "qty_out": o.qty_out,
        "contamination": o.contamination
    } for o in ops]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="operations")
    output.seek(0)
    fname = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, as_attachment=True, download_name=fname, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def register_api(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(species_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(batches_bp)
    app.register_blueprint(layout_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(qc_bp)
    app.register_blueprint(reports_bp)
