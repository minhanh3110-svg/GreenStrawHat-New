# LabApp – Quản lý phòng lab nuôi cấy mô (Flask)

## Chạy nhanh (dev)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python app.py init-db
python app.py create-user --username admin --password admin
python app.py
```
Mặc định truy cập: http://127.0.0.1:5000

## Deploy Render
- Có sẵn `render.yaml`, `Procfile`, `runtime.txt`
- Start command: `gunicorn app:app`
- Lần đầu: mở Shell chạy `python app.py init-db` + tạo user admin
