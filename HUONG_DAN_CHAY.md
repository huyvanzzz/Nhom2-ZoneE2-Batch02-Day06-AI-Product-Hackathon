# Huong Dan Chay Demo Vinmec AI Intake

File nay huong dan chay backend, frontend va public link bang VS Code Ports/Dev Tunnels.

## 1. Chay Backend

Mo terminal PowerShell tai thu muc goc repo:

```powershell
cd D:\VinM-Batch02-Day06-AI-Product-Hackathon\codebase\backend
python -m uvicorn vinm_backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend se chay tai:

```text
http://127.0.0.1:8000
```

Kiem tra backend:

```text
http://127.0.0.1:8000/docs
```

Neu vao duoc trang Swagger docs la backend dang chay.

## 2. Chay Frontend

Mo them mot terminal PowerShell khac:

```powershell
cd D:\VinM-Batch02-Day06-AI-Product-Hackathon\codebase\frontend
python -m http.server 4173
```

Frontend se chay tai:

```text
http://127.0.0.1:4173
```

## 3. Dang Nhap Dashboard Bac Si

Tren frontend, bam nut:

```text
Xem handoff cho bac si
```

Dung tai khoan demo:

```text
Ten bac si: Demo Doctor
Ma bac si: VINMEC-DR-01
```

Sau khi dang nhap, dashboard bac si se hien danh sach case, thong ke trong ngay va summary cho tung ca.

## 4. Public Cho Nguoi Khac Bang VS Code Ports

Neu dung VS Code Ports/Dev Tunnels, can public ca 2 port:

```text
4173  frontend
8000  backend
```

Vi du VS Code tao link:

```text
Frontend: https://rxzh1pv7-4173.jpe1.devtunnels.ms
Backend:  https://rxzh1pv7-8000.jpe1.devtunnels.ms
```

Khi gui cho nguoi khac, gui link frontend kem tham so `api` tro ve backend:

```text
https://rxzh1pv7-4173.jpe1.devtunnels.ms/?api=https://rxzh1pv7-8000.jpe1.devtunnels.ms
```

Ly do: frontend mac dinh goi backend local `127.0.0.1:8000`. Voi may nguoi nhan link, `127.0.0.1` la may cua ho, khong phai may cua ban. Tham so `?api=...` giup frontend goi dung backend tunnel cua ban.

## 5. Neu Nguoi Khac Thay Giao Dien Cu Hoac Tra Loi Khac

Thu cac buoc sau:

1. Tat server frontend cu va chay lai dung folder `codebase/frontend`.
2. Tat backend cu va chay lai dung folder `codebase/backend`.
3. Public lai ca port `4173` va `8000`.
4. Gui lai link frontend kem `?api=<backend-tunnel-url>`.
5. Bao nguoi nhan hard reload trinh duyet bang `Ctrl + F5` hoac mo tab an danh.

## 6. Kiem Tra Nhanh API

Mo:

```text
https://<backend-tunnel-url>/docs
```

Neu Swagger docs hien thi, backend public thanh cong.

Sau do mo:

```text
https://<frontend-tunnel-url>/?api=https://<backend-tunnel-url>
```

Neu chat tao session va dashboard bac si cap nhat case sau khi chat, hai phan frontend/backend da ket noi dung.

## 7. Luu Y

- Khong sua file `.env` khi demo.
- Neu can them bien moi, chi cap nhat `.env.example`.
- Backend luu case/log demo o local trong `codebase/backend/var/`.
- Logs chi nen xem local, khong hien truc tiep tren dashboard nguoi dung.
- Cac cau ngoai pham vi nhu gia vang, xin API key, hoac yeu cau phan biet chung toc se bi backend tu choi va khong cap nhat case.
