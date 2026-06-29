"""
A Piece of Eden — Backend (FastAPI + Supabase)
Upload file pakai httpx langsung ke Supabase Storage REST API
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, uuid, httpx
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL    = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY    = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
STORAGE_BUCKET  = os.getenv("SUPABASE_STORAGE_BUCKET", "payment-proofs")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="A Piece of Eden API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Upload file ke Supabase Storage ────────────────────────────────
def upload_to_supabase_storage(file_bytes: bytes, file_name: str, content_type: str) -> str:
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_name}"

    # Cetak URL di terminal agar mudah debug kalau ada masalah
    print(f"[DEBUG] SUPABASE_URL  = {SUPABASE_URL}")
    print(f"[DEBUG] Upload ke URL = {upload_url}")

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    response = httpx.post(upload_url, content=file_bytes, headers=headers)

    print(f"[DEBUG] Response status = {response.status_code}")
    print(f"[DEBUG] Response body   = {response.text}")

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=500,
            detail=f"Gagal upload file ke Supabase Storage: {response.text}"
        )

    return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{file_name}"


class ReservationStatus(BaseModel):
    status: str


# ── 1. SUBMIT RESERVASI ────────────────────────────────────────────
@app.post("/api/reservations")
async def create_reservation(
    name:              str        = Form(...),
    email:             str        = Form(...),
    phone:             str        = Form(...),
    event_date:        str        = Form(...),
    time_start:        str        = Form(...),
    time_end:          str        = Form(...),
    guests:            int        = Form(...),
    event_description: str        = Form(...),
    total_cost:        int        = Form(...),
    dp_amount:         int        = Form(...),
    payment_proof:     UploadFile = File(...)
):
    file_bytes   = await payment_proof.read()
    file_ext     = os.path.splitext(payment_proof.filename)[1]
    file_name    = f"{uuid.uuid4()}{file_ext}"
    content_type = payment_proof.content_type or "application/octet-stream"

    file_url = upload_to_supabase_storage(file_bytes, file_name, content_type)

    data = {
        "name":                   name,
        "email":                  email,
        "phone":                  phone,
        "event_date":             event_date,
        "time_start":             time_start,
        "time_end":               time_end,
        "guests":                 guests,
        "event_description":      event_description,
        "total_cost":             total_cost,
        "dp_amount":              dp_amount,
        "payment_proof_url":      file_url,
        "payment_proof_filename": file_name,
        "status":                 "pending",
    }

    response = supabase.table("reservations").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Gagal menyimpan reservasi ke database")

    saved = response.data[0]
    return {
        "success": True,
        "message": "Reservasi berhasil dikirim! Kami akan menghubungi Anda segera.",
        "reservation_id": saved["id"],
        "data": saved,
    }


# ── 2. LIHAT SEMUA RESERVASI ───────────────────────────────────────
@app.get("/api/reservations")
def list_reservations():
    response = supabase.table("reservations").select("*").order("created_at", desc=True).execute()
    return {"success": True, "total": len(response.data), "data": response.data}


# ── 3. LIHAT SATU RESERVASI ────────────────────────────────────────
@app.get("/api/reservations/{reservation_id}")
def get_reservation(reservation_id: str):
    response = supabase.table("reservations").select("*").eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "data": response.data[0]}


# ── 4. UPDATE STATUS ───────────────────────────────────────────────
@app.patch("/api/reservations/{reservation_id}/status")
def update_status(reservation_id: str, body: ReservationStatus):
    valid = ["pending", "confirmed", "cancelled"]
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status tidak valid. Pilih: {', '.join(valid)}")
    response = supabase.table("reservations").update({"status": body.status}).eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "message": f"Status diubah ke '{body.status}'", "data": response.data[0]}


# ── 5. CEK KETERSEDIAAN TANGGAL ────────────────────────────────────
@app.get("/api/availability")
def check_availability(date: str):
    response = supabase.table("reservations") \
        .select("id, status") \
        .eq("event_date", date) \
        .in_("status", ["pending", "confirmed"]) \
        .execute()
    return {"date": date, "available": len(response.data) == 0, "bookings_count": len(response.data)}
