# A Piece of Eden — Luxury Garden Venue
> Website reservasi venue garden mewah di Surabaya.

---

## Struktur Folder

```
A-Piece-of-Eden/
├── frontend/               ← File website (HTML, CSS, gambar)
│   ├── Index.html
│   ├── reserve.html
│   ├── style.css
│   ├── reserve.css
│   └── *.jpg / *.png
│
├── backend/                ← Server Python
│   ├── main.py             ← Server utama
│   ├── requirements.txt    ← Daftar library
│   ├── supabase_schema.sql ← SQL untuk setup database
│   └── .env                ← Konfigurasi rahasia (BUAT SENDIRI, jangan di-upload)
│
└── README.md
```

---

## Persiapan Awal (Lakukan Sekali Saja)

### 1. Install Python

Buka https://www.python.org/downloads/ dan download versi terbaru.

> **Penting saat instalasi:** centang kotak **"Add Python to PATH"** sebelum klik Install.

Verifikasi di Command Prompt:
```
python --version
```
Harus muncul angka versi, contoh: `Python 3.13.0`

---

### 2. Buka folder backend di Command Prompt

Buka File Explorer, masuk ke folder `A-Piece-of-Eden\backend`.
Klik kolom alamat di atas, ketik `cmd`, tekan Enter.

Command Prompt akan terbuka langsung di folder backend.

---

### 3. Buat Virtual Environment

Virtual environment = ruang terisolasi agar library project ini tidak tercampur dengan Python lain di laptop.

```
python -m venv venv
```

---

### 4. Aktifkan Virtual Environment

```
venv\Scripts\activate
```

Kalau berhasil, di awal baris Command Prompt akan muncul `(venv)`.

> Setiap kali buka Command Prompt baru, langkah ini harus diulang sebelum menjalankan server.

---

### 5. Install semua library

```
pip install -r requirements.txt
```

Tunggu sampai selesai. Ini hanya perlu dilakukan sekali.

---

### 6. Buat file `.env`

Di dalam folder `backend`, buat file baru bernama `.env` (titik di depan, tanpa ekstensi).

**Cara buat di Windows:**
1. Klik kanan di dalam folder `backend` → New → Text Document
2. Rename file tersebut menjadi `.env` (hapus `.txt` di belakangnya)
3. Kalau muncul peringatan soal ekstensi, klik Yes

Buka file `.env` dengan Notepad, isi dengan:
```
SUPABASE_URL=https://xxxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SUPABASE_STORAGE_BUCKET=payment-proofs
```

Ganti nilainya dengan data dari Supabase Dashboard → Project Settings → API.

> **Jangan pernah upload file `.env` ke GitHub.** File ini sudah terdaftar di `.gitignore`.

---

## Menjalankan Server

Setiap kali ingin menjalankan website, buka Command Prompt di folder `backend` dan jalankan:

```
venv\Scripts\activate
uvicorn main:app --reload
```

Kalau berhasil akan muncul:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Biarkan Command Prompt ini tetap terbuka** selama menggunakan website.

Untuk stop server: tekan `Ctrl + C`.

---

## Membuka Website

Setelah server berjalan, buka File Explorer → masuk ke folder `frontend` → double-click `Index.html`.

Browser akan membuka halaman utama website.

---

## Cek Server Berjalan

Buka browser, ketik di address bar:
```
http://localhost:8000/api/reservations
```

Kalau muncul `{"success": true, "total": 0, "data": []}` berarti server berjalan normal.

---

## Setup Database Supabase (Lakukan Sekali Saja)

1. Buka https://supabase.com → masuk ke project kamu
2. Klik **SQL Editor** di sidebar kiri
3. Klik **New query**
4. Buka file `backend/supabase_schema.sql` dengan Notepad
5. Copy semua isinya → Paste ke SQL Editor
6. Klik **Run**
7. Harus muncul: `Success. No rows returned`

---

## Setup Storage Supabase (Lakukan Sekali Saja)

1. Di Supabase Dashboard, klik **Storage** di sidebar kiri
2. Klik **New bucket**
3. Nama bucket: `payment-proofs`
4. Matikan toggle **Public bucket**
5. Klik **Save**

---

## Melihat Data Reservasi

Setelah ada yang submit form di website:

**Lewat browser:**
```
http://localhost:8000/api/reservations
```

**Lewat Supabase:**
Buka Supabase Dashboard → **Table Editor** → pilih tabel `reservations`.

**Bukti pembayaran:**
Buka Supabase Dashboard → **Storage** → `payment-proofs`.

---

## Troubleshooting

**`python` tidak dikenali:**
Python belum ditambahkan ke PATH. Uninstall Python, install ulang, dan centang "Add Python to PATH".

**`venv\Scripts\activate` tidak bisa dijalankan:**
Jalankan perintah ini dulu di PowerShell (bukan CMD) sebagai Administrator:
```
Set-ExecutionPolicy RemoteSigned
```
Lalu kembali ke CMD dan coba lagi.

**Muncul "Tidak dapat terhubung ke server":**
Server belum berjalan. Pastikan Command Prompt dengan `uvicorn` masih terbuka dan tidak ada error.

**Muncul error saat `pip install`:**
Pastikan virtual environment sudah aktif (ada tulisan `(venv)` di awal baris).

**Port 8000 sudah dipakai aplikasi lain:**
Jalankan server di port berbeda:
```
uvicorn main:app --reload --port 8001
```
Lalu ubah baris `const API_URL` di `frontend/reserve.html` menjadi `http://localhost:8001`.

---

## Tech Stack

| Bagian | Teknologi |
|--------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Database | Supabase (PostgreSQL) |
| File Storage | Supabase Storage |
| Server | Uvicorn |
