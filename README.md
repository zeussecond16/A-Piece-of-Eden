# 🌿 A Piece of Eden

> Website reservasi venue garden mewah di Surabaya, dibangun dengan arsitektur client-server modern.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Storage-3ECF8E?style=flat&logo=supabase&logoColor=white)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=flat&logo=vercel&logoColor=white)
![Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)

---

## Daftar Isi

- [Deskripsi](#deskripsi)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Struktur Folder](#struktur-folder)
- [Teknologi](#teknologi)
- [Cara Menjalankan Lokal](#cara-menjalankan-lokal)
- [REST API](#rest-api)
- [Deployment](#deployment)
- [Konfigurasi Environment](#konfigurasi-environment)

---

## Deskripsi

A Piece of Eden memisahkan frontend dan backend menjadi dua layanan yang berjalan secara independen dan berkomunikasi melalui REST API.

- **Frontend** menampilkan antarmuka kepada pengguna dan mengirim data ke backend.
- **Backend** menangani seluruh logika bisnis, validasi data, dan komunikasi dengan database.
- **Supabase** menyimpan seluruh data reservasi dan file bukti pembayaran.

Pendekatan ini memastikan database dan API Key tidak pernah terekspos ke sisi pengguna.

---

## Arsitektur Sistem

```
Pengguna (Browser)
       │
       ▼
┌─────────────────────────┐
│  Frontend               │  HTML · CSS · JavaScript
│  https://deploy-eden.vercel.app  │  Hosted on Vercel
└─────────────────────────┘
       │
       │  HTTP Request (REST API)
       ▼
┌─────────────────────────┐
│  Backend                │  Python · FastAPI · Uvicorn
│  https://grand-dedication-production-9d90.up.railway.app  │  Hosted on Railway
└─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Supabase               │  PostgreSQL · Storage
│  Database & File Storage│
└─────────────────────────┘
```

### Alur Request

```
1. Pengguna mengisi form reservasi di browser
2. JavaScript mengumpulkan data form + file bukti bayar
3. Frontend mengirim POST request ke backend Railway
4. Backend memvalidasi data yang diterima
5. Backend mengupload file ke Supabase Storage
6. Backend menyimpan data reservasi ke Supabase Database
7. Backend mengembalikan response JSON ke frontend
8. Frontend menampilkan notifikasi berhasil atau gagal kepada pengguna
```

---

## Struktur Folder

```
A-Piece-of-Eden/
│
├── frontend/                    ← File website
│   ├── index.html               ← Halaman utama
│   ├── reserve.html             ← Halaman form reservasi
│   ├── style.css                ← Stylesheet halaman utama
│   ├── reserve.css              ← Stylesheet halaman reservasi
│   └── *.jpg / *.png            ← Aset gambar
│
├── backend/                     ← Server API
│   ├── main.py                  ← Aplikasi FastAPI utama
│   ├── requirements.txt         ← Daftar dependensi Python
│   ├── supabase_schema.sql      ← SQL untuk setup tabel database
│   └── .env                     ← Konfigurasi rahasia (tidak di-upload ke Git)
│
├── .gitignore
└── README.md
```

---

## Teknologi

### Frontend
| Teknologi | Keterangan |
|-----------|------------|
| HTML5 | Struktur halaman |
| CSS3 | Styling dan animasi |
| Vanilla JavaScript | Logika form dan komunikasi API |

### Backend
| Library | Versi | Keterangan |
|---------|-------|------------|
| FastAPI | ≥ 0.115.5 | Web framework utama |
| Uvicorn | ≥ 0.30.0 | ASGI server |
| Pydantic | ≥ 2.11.0 | Validasi data |
| HTTPX | ≥ 0.28.1 | HTTP client untuk upload ke Supabase Storage |
| Python Multipart | ≥ 0.0.12 | Parsing form data dan file upload |
| Python Dotenv | ≥ 1.0.1 | Membaca file `.env` |
| Supabase | ≥ 2.15.3 | Client SDK untuk database |

### Infrastructure
| Layanan | Fungsi |
|---------|--------|
| Supabase | Database PostgreSQL + File Storage |
| Vercel | Hosting frontend |
| Railway | Hosting backend |

---

## Cara Menjalankan Lokal

### Prasyarat

- Python 3.11 atau lebih baru → https://www.python.org/downloads/
- Akun Supabase → https://supabase.com

> **Windows:** Saat instalasi Python, centang kotak **"Add Python to PATH"**.

---

### 1. Clone repository

```bash
git clone https://github.com/username/A-Piece-of-Eden.git
cd A-Piece-of-Eden
```

---

### 2. Setup backend

Masuk ke folder backend:

```bash
cd backend
```

Buat virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependensi:

```bash
pip install -r requirements.txt
```

---

### 3. Buat file `.env`

Buat file `.env` di dalam folder `backend/` dengan isi berikut:

```env
SUPABASE_URL=https://xxxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SUPABASE_STORAGE_BUCKET=payment-proofs
```

Nilai-nilai ini didapat dari **Supabase Dashboard → Project Settings → API**.

> ⚠️ Jangan pernah upload file `.env` ke GitHub. File ini sudah terdaftar di `.gitignore`.

---

### 4. Setup database Supabase (sekali saja)

1. Buka Supabase Dashboard → **SQL Editor** → **New query**
2. Copy seluruh isi file `backend/supabase_schema.sql`
3. Paste ke SQL Editor → klik **Run**

Buat bucket storage:

1. Buka **Storage** → **New bucket**
2. Nama: `payment-proofs`
3. Matikan toggle **Public bucket** → **Save**

---

### 5. Jalankan server

```bash
uvicorn main:app --reload
```

Server berjalan di `http://localhost:8000`.

Verifikasi dengan membuka browser:

```
http://localhost:8000/api/reservations
```

Harus muncul: `{"success": true, "total": 0, "data": []}`

---

### 6. Buka frontend

Buka file `frontend/index.html` langsung di browser (double-click).

> Pastikan terminal yang menjalankan `uvicorn` tetap terbuka selama menggunakan website.

---

## REST API

Base URL (lokal): `http://localhost:8000`  
Base URL (production): `https://grand-dedication-production-9d90.up.railway.app`

---

### `POST /api/reservations`

Membuat reservasi baru.

**Request** — `multipart/form-data`

| Field | Tipe | Keterangan |
|-------|------|------------|
| `name` | string | Nama lengkap pemesan |
| `email` | string | Email pemesan |
| `phone` | string | Nomor telepon |
| `event_date` | string | Tanggal acara (YYYY-MM-DD) |
| `time_start` | string | Jam mulai (HH:MM) |
| `time_end` | string | Jam selesai (HH:MM) |
| `guests` | integer | Jumlah tamu |
| `event_description` | string | Deskripsi acara |
| `total_cost` | integer | Total biaya (Rupiah) |
| `dp_amount` | integer | DP 30% (Rupiah) |
| `payment_proof` | file | Bukti pembayaran (gambar/PDF) |

**Response sukses** `200 OK`

```json
{
  "success": true,
  "message": "Reservasi berhasil dikirim! Kami akan menghubungi Anda segera.",
  "reservation_id": "uuid-string",
  "data": { ... }
}
```

---

### `GET /api/reservations`

Mengambil seluruh data reservasi.

**Response** `200 OK`

```json
{
  "success": true,
  "total": 5,
  "data": [ ... ]
}
```

---

### `GET /api/reservations/{id}`

Mengambil detail satu reservasi berdasarkan ID.

---

### `PATCH /api/reservations/{id}/status`

Mengubah status reservasi.

**Request body** — `application/json`

```json
{ "status": "confirmed" }
```

Nilai status yang valid: `pending` · `confirmed` · `cancelled`

---

### `GET /api/availability?date=YYYY-MM-DD`

Mengecek ketersediaan tanggal.

**Response** `200 OK`

```json
{
  "date": "2025-12-25",
  "available": true,
  "bookings_count": 0
}
```

---

## Deployment

### Frontend — Vercel

1. Push project ke GitHub
2. Buka https://vercel.com → **Add New Project** → import repository
3. Atur **Root Directory** ke `frontend`
4. Framework Preset: **Other**
5. Klik **Deploy**

Setelah selesai, Vercel memberikan domain publik, contoh:  
`https://deploy-eden.vercel.app`

---

### Backend — Railway

1. Push project ke GitHub
2. Buka https://railway.app → **New Project** → **Deploy from GitHub repo**
3. Pilih repository → atur **Root Directory** ke `backend`
4. Buka tab **Variables**, tambahkan:

| Variable | Nilai |
|----------|-------|
| `SUPABASE_URL` | `https://xxxxxxxxxxxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGci...` |
| `SUPABASE_STORAGE_BUCKET` | `payment-proofs` |

5. Buka tab **Settings** → **Start Command**, isi dengan:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Setelah selesai, Railway memberikan domain publik, contoh:  
`https://grand-dedication-production-9d90.up.railway.app`

---

### Menghubungkan Frontend dan Backend

Setelah keduanya di-deploy, pastikan dua hal ini sudah benar:

**1. `frontend/reserve.html`** — URL backend harus mengarah ke Railway:

```javascript
const API_URL = "https://grand-dedication-production-9d90.up.railway.app";
```

**2. `backend/main.py`** — URL frontend harus terdaftar di CORS tanpa trailing slash:

```python
allow_origins=["https://deploy-eden.vercel.app"],
```

> ⚠️ `SUPABASE_URL` di Railway **harus** berformat `https://xxxx.supabase.co` — tanpa `/rest/v1/` atau slash apapun di belakangnya.

---

## Konfigurasi Environment

| Variable | Keterangan | Contoh |
|----------|------------|--------|
| `SUPABASE_URL` | URL project Supabase | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key dari Supabase API settings | `eyJhbGci...` |
| `SUPABASE_STORAGE_BUCKET` | Nama bucket Supabase Storage | `payment-proofs` |

Nilai-nilai ini didapat dari **Supabase Dashboard → Project Settings → API**.

---

## Lisensi

Project ini dibuat untuk keperluan bisnis **A Piece of Eden**. Seluruh hak cipta dilindungi.
