"""
=============================================================
  A Piece of Eden — Backend API (FastAPI + Python)
  File: backend/main.py
=============================================================
  Semua data dikirim ke sini dulu.
  Nanti saat porting ke Supabase, ganti bagian yang
  ditandai komentar # [SUPABASE] dengan Supabase client.
=============================================================
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import uuid
import json
import shutil
from datetime import datetime

# ─────────────────────────────────────────────
#  SETUP APLIKASI
# ─────────────────────────────────────────────
app = FastAPI(
    title="A Piece of Eden API",
    description="Backend API untuk reservasi A Piece of Eden",
    version="1.0.0"
)

# Izinkan frontend mengakses backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # saat production: ganti * dengan domain asli
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder untuk menyimpan file upload
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# File JSON sebagai database sementara (ganti dengan Supabase nanti)
DB_FILE = "reservations_db.json"


# ─────────────────────────────────────────────
#  DATABASE LOKAL SEMENTARA (JSON)
#  [SUPABASE] Bagian ini akan diganti dengan
#             Supabase client saat porting
# ─────────────────────────────────────────────

def load_db() -> list:
    """Membaca semua data reservasi dari file JSON lokal."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data: list):
    """Menyimpan semua data reservasi ke file JSON lokal."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_reservation(reservation: dict) -> dict:
    """
    Menyimpan satu data reservasi baru.
    
    [SUPABASE] Ganti fungsi ini dengan:
    
        response = supabase.table("reservations").insert(reservation).execute()
        return response.data[0]
    """
    db = load_db()
    reservation["id"] = str(uuid.uuid4())
    reservation["created_at"] = datetime.now().isoformat()
    reservation["status"] = "pending"     # pending | confirmed | cancelled
    db.append(reservation)
    save_db(db)
    return reservation

def get_all_reservations() -> list:
    """
    Mengambil semua data reservasi.
    
    [SUPABASE] Ganti fungsi ini dengan:
    
        response = supabase.table("reservations").select("*").execute()
        return response.data
    """
    return load_db()

def get_reservation_by_id(reservation_id: str) -> Optional[dict]:
    """
    Mengambil satu reservasi berdasarkan ID.
    
    [SUPABASE] Ganti fungsi ini dengan:
    
        response = supabase.table("reservations").select("*").eq("id", reservation_id).execute()
        return response.data[0] if response.data else None
    """
    db = load_db()
    for item in db:
        if item["id"] == reservation_id:
            return item
    return None

def update_reservation_status(reservation_id: str, status: str) -> Optional[dict]:
    """
    Mengubah status reservasi.
    
    [SUPABASE] Ganti fungsi ini dengan:
    
        response = supabase.table("reservations").update({"status": status}).eq("id", reservation_id).execute()
        return response.data[0] if response.data else None
    """
    db = load_db()
    for item in db:
        if item["id"] == reservation_id:
            item["status"] = status
            save_db(db)
            return item
    return None


# ─────────────────────────────────────────────
#  MODEL DATA (bentuk data yang diterima API)
# ─────────────────────────────────────────────

class ReservationStatus(BaseModel):
    status: str   # "pending" | "confirmed" | "cancelled"


# ─────────────────────────────────────────────
#  ENDPOINT API
# ─────────────────────────────────────────────

@app.get("/")
def root():
    """Cek apakah server berjalan."""
    return {"message": "A Piece of Eden API berjalan ✓", "version": "1.0.0"}


# ── 1. SUBMIT RESERVASI ──────────────────────
@app.post("/api/reservations")
async def create_reservation(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    event_date: str = Form(...),
    time_start: str = Form(...),
    time_end: str = Form(...),
    guests: int = Form(...),
    event_description: str = Form(...),
    total_cost: int = Form(...),
    dp_amount: int = Form(...),
    payment_proof: UploadFile = File(...)
):
    """
    Menerima data form reservasi dari halaman reserve.html.
    
    Data yang diterima:
    - name           : nama lengkap pemesan
    - email          : email pemesan
    - phone          : nomor telepon
    - event_date     : tanggal acara (format: YYYY-MM-DD)
    - time_start     : jam mulai (format: HH:MM)
    - time_end       : jam selesai (format: HH:MM)
    - guests         : jumlah tamu
    - event_description : deskripsi acara
    - total_cost     : total biaya (dalam Rupiah, angka)
    - dp_amount      : jumlah DP 30% (dalam Rupiah, angka)
    - payment_proof  : file bukti pembayaran (gambar/PDF)
    """

    # ── Simpan file bukti pembayaran ──
    file_ext = os.path.splitext(payment_proof.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(payment_proof.file, buffer)

    # ── Susun data reservasi ──
    reservation_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "event_date": event_date,
        "time_start": time_start,
        "time_end": time_end,
        "guests": guests,
        "event_description": event_description,
        "total_cost": total_cost,
        "dp_amount": dp_amount,
        # [SUPABASE] Untuk Supabase Storage, simpan URL publik file-nya
        # Contoh: payment_proof_url = upload_to_supabase_storage(file_path)
        "payment_proof_filename": file_name,
        "payment_proof_original": payment_proof.filename,
    }

    # ── Simpan ke database ──
    saved = add_reservation(reservation_data)

    return {
        "success": True,
        "message": "Reservasi berhasil dikirim! Kami akan menghubungi Anda segera.",
        "reservation_id": saved["id"],
        "data": saved
    }


# ── 2. LIHAT SEMUA RESERVASI (untuk admin) ──
@app.get("/api/reservations")
def list_reservations():
    """
    Mengambil semua data reservasi.
    Endpoint ini untuk halaman admin.
    """
    reservations = get_all_reservations()
    return {
        "success": True,
        "total": len(reservations),
        "data": reservations
    }


# ── 3. LIHAT SATU RESERVASI ──
@app.get("/api/reservations/{reservation_id}")
def get_reservation(reservation_id: str):
    """Mengambil detail satu reservasi berdasarkan ID."""
    reservation = get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "data": reservation}


# ── 4. UPDATE STATUS RESERVASI (untuk admin) ──
@app.patch("/api/reservations/{reservation_id}/status")
def update_status(reservation_id: str, body: ReservationStatus):
    """
    Mengubah status reservasi.
    Status yang valid: pending | confirmed | cancelled
    """
    valid_statuses = ["pending", "confirmed", "cancelled"]
    if body.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status tidak valid. Pilih: {', '.join(valid_statuses)}"
        )

    updated = update_reservation_status(reservation_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")

    return {"success": True, "message": f"Status diubah ke '{body.status}'", "data": updated}


# ── 5. CEK KETERSEDIAAN TANGGAL ──
@app.get("/api/availability")
def check_availability(date: str):
    """
    Mengecek apakah tanggal tertentu sudah ada reservasi yang confirmed.
    Parameter: date (format: YYYY-MM-DD)
    Frontend bisa pakai ini saat user pilih tanggal di form.
    """
    reservations = get_all_reservations()
    booked = [
        r for r in reservations
        if r.get("event_date") == date and r.get("status") in ["pending", "confirmed"]
    ]

    return {
        "date": date,
        "available": len(booked) == 0,
        "bookings_count": len(booked)
    }


# ─────────────────────────────────────────────
#  SAJIKAN FRONTEND DARI FOLDER ../frontend
# ─────────────────────────────────────────────
# Uncomment baris di bawah kalau mau backend juga
# serve file HTML/CSS/gambar frontend-nya langsung.
# Pastikan ada folder "frontend" di samping folder "backend".

# app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# @app.get("/{path:path}")
# def serve_frontend(path: str):
#     file_path = f"../frontend/{path}"
#     if os.path.exists(file_path):
#         return FileResponse(file_path)
#     return FileResponse("../frontend/Index.html")
