from flask import Blueprint, jsonify, request
from extensions import db
from models import Batch, BatchOperation

bp = Blueprint("batches_api", __name__, url_prefix="/api/batches")

@bp.get("")
def list_batches():
    rows = Batch.query.order_by(Batch.id.desc()).limit(200).all()
    return jsonify([{
        "id": b.id, "code": b.code, "stage": b.stage, "status": b.status
    } for b in rows])

@bp.post("")
def create_batch():
    data = request.get_json(force=True)
    b = Batch(code=data["code"], species_id=data["species_id"], stage=data.get("stage"))
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id, "code": b.code}), 201

@bp.post("/<int:batch_id>/ops")
def create_op(batch_id):
    data = request.get_json(force=True)
    op = BatchOperation(batch_id=batch_id, op_type=data["op_type"],
                        qty_in=data.get("qty_in"), qty_out=data.get("qty_out"),
                        contamination=data.get("contamination"))
    db.session.add(op)
    db.session.commit()
    return jsonify({"id": op.id}), 201
