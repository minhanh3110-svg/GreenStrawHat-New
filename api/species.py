from flask import Blueprint, jsonify, request
from extensions import db
from models import Species

bp = Blueprint("species_api", __name__, url_prefix="/api/species")

@bp.get("")
def list_species():
    rows = Species.query.order_by(Species.id.desc()).limit(200).all()
    return jsonify([{
        "id": s.id, "code": s.code, "name_vi": s.name_vi,
        "name_en": s.name_en, "cultivar": s.cultivar
    } for s in rows])

@bp.post("")
def create_species():
    data = request.get_json(force=True)
    s = Species(code=data["code"], name_vi=data["name_vi"],
                name_en=data.get("name_en"), cultivar=data.get("cultivar"))
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id, "code": s.code}), 201
