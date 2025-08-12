# LabApp – Quản lý phòng lab nuôi cấy mô (Flask)

## Chạy nhanh (dev)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # Hoặc tự tạo file .env

# Khởi tạo DB + tạo user admin
python app.py init-db
python app.py create-user --username admin --password admin

# Chạy app
python app.py
# Mặc định: http://127.0.0.1:5000
```
Đăng nhập: **admin / admin** (hãy đổi mật khẩu sau khi đăng nhập).


---

## Triển khai lên GitHub & Render

### 1) Đưa mã lên GitHub
```bash
# Tại thư mục dự án (labapp)
git init
git add .
git commit -m "init labapp"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

> Lưu ý: File nhạy cảm (.env, database.db, v.v.) đã được `.gitignore` bỏ qua.

### 2) Deploy Render (cách A: dùng Dashboard)
1. Vào **render.com** → New + → **Web Service** → Connect GitHub repo vừa push.
2. Runtime: **Python**.  
   Build Command: `pip install -r requirements.txt`  
   Start Command: `gunicorn app:app`
3. Thêm biến môi trường (Environment):
   - `SECRET_KEY` = giá trị ngẫu nhiên
   - (Tuỳ chọn) `SQLALCHEMY_DATABASE_URI` = dùng PostgreSQL (khuyến nghị prod)
4. Deploy. Sau khi chạy xong, mở URL dịch vụ → `/auth/login`.

### 2') Deploy Render (cách B: dùng **render.yaml**)
- Vào **render.com** → **Blueprints** → New Blueprint → trỏ tới repo chứa `render.yaml`.
- Render sẽ tạo **Web Service** + **PostgreSQL** (free plan).  
- Sau khi tạo xong, vào **Environment** của Web Service →
  - Sửa `SQLALCHEMY_DATABASE_URI` thành chuỗi kết nối của database Postgres được tạo (Internal URL).
- **Khởi tạo DB**: mở tab **Shell** của service và chạy:
```bash
python app.py init-db
python app.py create-user --username admin --password <mật-khẩu>
```

### 3) Dùng PostgreSQL trên Render (khuyến nghị)
- Trong Web Service → **Environment**:
  - `SQLALCHEMY_DATABASE_URI` = `<Postgres Internal Connection String>` (ví dụ: `postgresql://user:pass@host:5432/db`)
- Khởi tạo schema như trên.
- Khi đổi DB, dữ liệu SQLite cũ không tự chuyển sang – cần migrate bằng script nếu muốn.

### 4) Auto Deploy
- Bật **Auto Deploy** trong Render để tự build khi bạn push code lên GitHub.

---

## Ghi chú sản xuất
- Bật **Gunicorn** (đã dùng Procfile).  
- Thêm HTTPS & domain tùy chỉnh trong Render.  
- Tách **migrations/** nếu dùng Flask-Migrate/Alembic (hiện bản demo dùng `create_all`).  
- Thêm logging JSON, audit, và backups Postgres cho môi trường thật.
