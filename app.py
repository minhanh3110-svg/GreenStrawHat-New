import os, io
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from openpyxl import Workbook

# --------- App & Config ---------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACKING_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --------- RBAC helper ---------
def require_roles(*roles):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))
            if current_user.role not in ("admin",) + tuple(roles):
                flash("Bạn không có quyền truy cập mục này.", "danger")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# --------- Models ---------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="viewer")  # admin, cay, sang, moitruong, viewer

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class CayLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngay = db.Column(db.Date, default=date.today)
    thu = db.Column(db.String(10))
    tuan = db.Column(db.Integer)
    thang = db.Column(db.Integer)
    nguoi = db.Column(db.String(80))
    ma_nguoi = db.Column(db.String(30))
    box = db.Column(db.String(30))
    tinh_trang = db.Column(db.String(10))  # Sạch/Khuẩn
    chu_ky = db.Column(db.String(10))      # Nhân/Giãn/Rễ
    moi_truong_me = db.Column(db.String(120))
    so_tui_me = db.Column(db.Integer, default=0)
    so_cum_tui_me = db.Column(db.Integer, default=0)
    tong_cum_me = db.Column(db.Integer, default=0)
    so_tui_con = db.Column(db.Integer, default=0)
    so_cum_tui_con = db.Column(db.Integer, default=0)
    tong_cum_con = db.Column(db.Integer, default=0)
    giong = db.Column(db.String(80))
    lo_nhan = db.Column(db.String(80))
    tong_gio = db.Column(db.Float, default=0.0)
    nang_suat = db.Column(db.Float, default=0.0)

class SangLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngay = db.Column(db.Date, default=date.today)
    thu = db.Column(db.String(10))
    tuan = db.Column(db.Integer)
    thang = db.Column(db.Integer)
    nguoi = db.Column(db.String(80))
    ma_nguoi = db.Column(db.String(30))
    ke = db.Column(db.String(30))
    tinh_trang = db.Column(db.String(20))
    chu_ky = db.Column(db.String(10))
    ghi_chu = db.Column(db.Text)
    tong_gio = db.Column(db.Float, default=0.0)

class MoiTruongLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngay = db.Column(db.Date, default=date.today)
    thu = db.Column(db.String(10))
    tuan = db.Column(db.Integer)
    thang = db.Column(db.Integer)
    nguoi = db.Column(db.String(80))
    ma_nguoi = db.Column(db.String(30))
    noi_dung = db.Column(db.String(200))  # chế môi trường, hấp khử, v.v.
    so_mau = db.Column(db.Integer, default=0)
    tong_gio = db.Column(db.Float, default=0.0)
    ghi_chu = db.Column(db.Text)

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

# --------- Auto init (first run) ---------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

# --------- Auth Views ---------
@app.route("/auth/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        u = User.query.filter_by(username=username).first()
        if u and u.check_password(password):
            login_user(u, remember=True)
            return redirect(url_for("index"))
        flash("Sai tài khoản hoặc mật khẩu.", "danger")
    return render_template("auth/login.html")

@app.get("/auth/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --------- Home ---------
@app.get("/")
@login_required
def index():
    return render_template("index.html")

# --------- Helpers ---------
def xlsx_from_rows(headers, rows, title="Data"):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append(headers)
    for r in rows: ws.append(r)
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return buf

# --------- Phòng cấy ---------
@app.route("/cay", methods=["GET","POST"])
@require_roles("cay")
def cay_page():
    if request.method == "POST":
        f = request.form
        so_tui_me = int(f.get("so_tui_me",0) or 0)
        so_cum_tui_me = int(f.get("so_cum_tui_me",0) or 0)
        so_tui_con = int(f.get("so_tui_con",0) or 0)
        so_cum_tui_con = int(f.get("so_cum_tui_con",0) or 0)
        tong_cum_me = so_tui_me * so_cum_tui_me
        tong_cum_con = so_tui_con * so_cum_tui_con
        tong_gio = float(f.get("tong_gio",0) or 0)
        nang_suat = (tong_cum_me / tong_gio) if tong_gio>0 else 0

        log = CayLog(
            ngay = datetime.strptime(f.get("ngay"), "%Y-%m-%d").date(),
            thu = f.get("thu"), tuan = int(f.get("tuan") or 0), thang = int(f.get("thang") or 0),
            nguoi = f.get("nguoi"), ma_nguoi = f.get("ma_nguoi"), box = f.get("box"),
            tinh_trang = f.get("tinh_trang"), chu_ky = f.get("chu_ky"),
            moi_truong_me = f.get("moi_truong_me"),
            so_tui_me = so_tui_me, so_cum_tui_me = so_cum_tui_me, tong_cum_me = tong_cum_me,
            so_tui_con = so_tui_con, so_cum_tui_con = so_cum_tui_con, tong_cum_con = tong_cum_con,
            giong = f.get("giong"), lo_nhan = f.get("lo_nhan"),
            tong_gio = tong_gio, nang_suat = nang_suat
        )
        db.session.add(log); db.session.commit()
        flash("Đã lưu nhật ký phòng cấy.", "success")
        return redirect(url_for("cay_page"))
    rows = CayLog.query.order_by(CayLog.id.desc()).limit(500).all()
    return render_template("cay/index.html", rows=rows)

@app.get("/cay/export")
@require_roles("cay")
def cay_export():
    headers = ["Ngày","Thứ","Tuần","Tháng","Người","Mã người","Box","Tình trạng","Chu kỳ","MT mô mẹ",
               "Số túi mẹ","Cụm/túi mẹ","Tổng cụm mẹ","Số túi con","Cụm/túi con","Tổng cụm con",
               "Giống","Lô nhận","Tổng giờ","Năng suất"]
    rows = []
    for r in CayLog.query.order_by(CayLog.id).all():
        rows.append([r.ngay.isoformat(), r.thu, r.tuan, r.thang, r.nguoi, r.ma_nguoi, r.box, r.tinh_trang, r.chu_ky,
                     r.moi_truong_me, r.so_tui_me, r.so_cum_tui_me, r.tong_cum_me,
                     r.so_tui_con, r.so_cum_tui_con, r.tong_cum_con, r.giong, r.lo_nhan, r.tong_gio, r.nang_suat])
    buf = xlsx_from_rows(headers, rows, "Cay")
    return send_file(buf, as_attachment=True, download_name="nhatky_cay.xlsx")

# --------- Phòng sáng ---------
@app.route("/sang", methods=["GET","POST"])
@require_roles("sang")
def sang_page():
    if request.method == "POST":
        f = request.form
        log = SangLog(
            ngay = datetime.strptime(f.get("ngay"), "%Y-%m-%d").date(),
            thu = f.get("thu"), tuan = int(f.get("tuan") or 0), thang = int(f.get("thang") or 0),
            nguoi = f.get("nguoi"), ma_nguoi = f.get("ma_nguoi"),
            ke = f.get("ke"), tinh_trang = f.get("tinh_trang"),
            chu_ky = f.get("chu_ky"), ghi_chu = f.get("ghi_chu"),
            tong_gio = float(f.get("tong_gio",0) or 0)
        )
        db.session.add(log); db.session.commit()
        flash("Đã lưu nhật ký phòng sáng.", "success")
        return redirect(url_for("sang_page"))
    rows = SangLog.query.order_by(SangLog.id.desc()).limit(500).all()
    return render_template("sang/index.html", rows=rows)

@app.get("/sang/export")
@require_roles("sang")
def sang_export():
    headers = ["Ngày","Thứ","Tuần","Tháng","Người","Mã người","Kệ","Tình trạng","Chu kỳ","Ghi chú","Tổng giờ"]
    rows = []
    for r in SangLog.query.order_by(SangLog.id).all():
        rows.append([r.ngay.isoformat(), r.thu, r.tuan, r.thang, r.nguoi, r.ma_nguoi, r.ke, r.tinh_trang, r.chu_ky, r.ghi_chu, r.tong_gio])
    buf = xlsx_from_rows(headers, rows, "Sang")
    return send_file(buf, as_attachment=True, download_name="nhatky_sang.xlsx")

# --------- Phòng môi trường ---------
@app.route("/moitruong", methods=["GET","POST"])
@require_roles("moitruong")
def moitruong_page():
    if request.method == "POST":
        f = request.form
        log = MoiTruongLog(
            ngay = datetime.strptime(f.get("ngay"), "%Y-%m-%d").date(),
            thu = f.get("thu"), tuan = int(f.get("tuan") or 0), thang = int(f.get("thang") or 0),
            nguoi = f.get("nguoi"), ma_nguoi = f.get("ma_nguoi"),
            noi_dung = f.get("noi_dung"), so_mau = int(f.get("so_mau") or 0),
            tong_gio = float(f.get("tong_gio",0) or 0), ghi_chu = f.get("ghi_chu")
        )
        db.session.add(log); db.session.commit()
        flash("Đã lưu nhật ký phòng môi trường.", "success")
        return redirect(url_for("moitruong_page"))
    rows = MoiTruongLog.query.order_by(MoiTruongLog.id.desc()).limit(500).all()
    return render_template("moi_truong/index.html", rows=rows)

@app.get("/moitruong/export")
@require_roles("moitruong")
def moitruong_export():
    headers = ["Ngày","Thứ","Tuần","Tháng","Người","Mã người","Nội dung","Số mẫu","Tổng giờ","Ghi chú"]
    rows = []
    for r in MoiTruongLog.query.order_by(MoiTruongLog.id).all():
        rows.append([r.ngay.isoformat(), r.thu, r.tuan, r.thang, r.nguoi, r.ma_nguoi, r.noi_dung, r.so_mau, r.tong_gio, r.ghi_chu])
    buf = xlsx_from_rows(headers, rows, "MoiTruong")
    return send_file(buf, as_attachment=True, download_name="nhatky_moitruong.xlsx")

# --------- Run ---------
if __name__ == "__main__":
    app.run(debug=True)
