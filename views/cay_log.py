from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date
from sqlalchemy import desc, func
from extensions import db
from models import InoculationLog

bp = Blueprint("caylog", __name__, url_prefix="/cay/nhat-ky-cay")

STATUS_CHOICES = [("CLEAN","Sạch"), ("CONTAM","Khuẩn")]
CYCLE_CHOICES  = [("NHAN","Nhân"), ("GIAN","Giãn"), ("RE","Rễ")]

@bp.route("/")
@login_required
def index():
    dfrom = request.args.get("from") or date.today().strftime("%Y-%m-01")
    dto   = request.args.get("to")   or date.today().strftime("%Y-%m-%d")
    q = (InoculationLog.query
         .filter(InoculationLog.date >= dfrom)
         .filter(InoculationLog.date <= dto)
         .order_by(desc(InoculationLog.id)))
    rows = q.limit(2000).all()
    return render_template("cay/inoc_list.html", rows=rows, dfrom=dfrom, dto=dto)

@bp.route("/new", methods=["GET","POST"])
@login_required
def create():
    if request.method == "POST":
        f = request.form
        log = InoculationLog(
            date = datetime.strptime(f["date"], "%Y-%m-%d").date(),
            operator_code = f["operator_code"].strip(),
            box_code   = f.get("box_code") or None,
            status     = f["status"],
            cycle      = f["cycle"],
            mother_media = f.get("mother_media") or None,
            mother_bag_count = int(f.get("mother_bag_count") or 0),
            clusters_per_bag = int(f.get("clusters_per_bag") or 0),
            child_bag_count  = int(f.get("child_bag_count") or 0),
            child_clusters_per_bag = int(f.get("child_clusters_per_bag") or 0),
            species_code  = f["species_code"].strip(),
            species_label = f.get("species_label") or None,
            received_lot  = f.get("received_lot") or None,
            total_hours   = float(f.get("total_hours") or 0),
            notes = f.get("notes") or None,
            batch_id = int(f["batch_id"]) if f.get("batch_id") else None,
        )
        db.session.add(log)
        db.session.commit()
        flash("Đã lưu nhật ký cấy.", "success")
        return redirect(url_for("caylog.index"))
    today = date.today().strftime("%Y-%m-%d")
    return render_template("cay/inoc_form.html",
                           STATUS_CHOICES=STATUS_CHOICES, CYCLE_CHOICES=CYCLE_CHOICES,
                           today=today)

@bp.post("/<int:log_id>/delete")
@login_required
def delete(log_id):
    row = InoculationLog.query.get_or_404(log_id)
    db.session.delete(row)
    db.session.commit()
    flash("Đã xoá bản ghi.", "info")
    return redirect(url_for("caylog.index"))

@bp.get("/nang-suat")
@login_required
def productivity():
    dfrom = request.args.get("from") or date.today().strftime("%Y-%m-01")
    dto   = request.args.get("to")   or date.today().strftime("%Y-%m-%d")
    rows = (db.session.query(
                InoculationLog.date.label("ngay"),
                InoculationLog.cycle.label("chu_ky"),
                func.sum((InoculationLog.child_bag_count * InoculationLog.child_clusters_per_bag)).label("tong_cum_con"),
                func.sum(InoculationLog.total_hours).label("tong_gio"))
            .filter(InoculationLog.date >= dfrom)
            .filter(InoculationLog.date <= dto)
            .group_by(InoculationLog.date, InoculationLog.cycle)
            .order_by(InoculationLog.date)
            .all())
    data = []
    for r in rows:
        cum = int(r.tong_cum_con or 0)
        gio = float(r.tong_gio or 0.0)
        ns_gio = (cum / gio) if gio > 0 else None
        data.append({"ngay": r.ngay, "chu_ky": r.chu_ky, "tong_cum_con": cum,
                     "tong_gio": round(gio,2), "nang_suat_cum_gio": round(ns_gio,2) if ns_gio else None})
    return render_template("cay/inoc_productivity.html", data=data, dfrom=dfrom, dto=dto)
