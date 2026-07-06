from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, uuid, httpx
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY         = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY    = os.getenv("SUPABASE_ANON_KEY")
STORAGE_BUCKET       = os.getenv("SUPABASE_STORAGE_BUCKET", "payment-proofs")
ADMIN_REGISTER_CODE  = os.getenv("ADMIN_REGISTER_CODE", "")

# Client "service role" -> akses penuh ke database (dipakai untuk operasi data)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Client "anon" -> khusus untuk proses autentikasi (register/login/verifikasi token)
supabase_auth: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI(title="A Piece of Eden API", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deploy-eden.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def upload_to_supabase_storage(file_bytes: bytes, file_name: str, content_type: str) -> str:
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_name}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": content_type,
        "x-upsert": "true",
    }
    response = httpx.post(upload_url, content=file_bytes, headers=headers)
    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=500,
            detail=f"Gagal upload file ke Supabase Storage: {response.text}"
        )
    return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{file_name}"


# ═══════════════════════════════════════════════════════════════
#  AUTENTIKASI ADMIN
# ═══════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    email: str
    password: str
    register_code: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ReservationStatus(BaseModel):
    status: str


class AdminNotesUpdate(BaseModel):
    admin_notes: str


def get_current_admin(authorization: str = Header(None)):
    """Dependency untuk memproteksi endpoint admin. Memverifikasi Bearer token
    dari Supabase Auth yang dikirim lewat header Authorization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak ditemukan. Silakan login kembali.")

    token = authorization.split(" ", 1)[1]
    try:
        user_response = supabase_auth.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau sudah kedaluwarsa. Silakan login kembali.")

    if not user_response or not user_response.user:
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau sudah kedaluwarsa. Silakan login kembali.")

    return user_response.user


@app.post("/api/auth/register")
async def register_admin(body: RegisterRequest):
    if not ADMIN_REGISTER_CODE or body.register_code != ADMIN_REGISTER_CODE:
        raise HTTPException(status_code=403, detail="Kode registrasi admin tidak valid.")

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password minimal 6 karakter.")

    try:
        result = supabase_auth.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registrasi gagal: {str(e)}")

    if not result.user:
        raise HTTPException(status_code=400, detail="Registrasi gagal. Coba lagi.")

    return {
        "success": True,
        "message": "Akun admin berhasil dibuat. Jika verifikasi email aktif di Supabase, cek inbox terlebih dahulu sebelum login.",
        "email": result.user.email,
    }


@app.post("/api/auth/login")
async def login_admin(body: LoginRequest):
    try:
        result = supabase_auth.auth.sign_in_with_password({"email": body.email, "password": body.password})
    except Exception:
        raise HTTPException(status_code=401, detail="Email atau password salah.")

    if not result.session:
        raise HTTPException(status_code=401, detail="Email atau password salah.")

    return {
        "success": True,
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "expires_in": result.session.expires_in,
        "email": result.user.email,
    }


@app.get("/api/auth/me")
def get_me(current_admin=Depends(get_current_admin)):
    return {"success": True, "email": current_admin.email}


# ═══════════════════════════════════════════════════════════════
#  RESERVASI (endpoint publik untuk tamu)
# ═══════════════════════════════════════════════════════════════

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


@app.get("/api/availability")
def check_availability(date: str):
    response = supabase.table("reservations") \
        .select("id, status") \
        .eq("event_date", date) \
        .in_("status", ["pending", "confirmed"]) \
        .execute()
    return {"date": date, "available": len(response.data) == 0, "bookings_count": len(response.data)}


# ═══════════════════════════════════════════════════════════════
#  RESERVASI (endpoint khusus admin — wajib login)
# ═══════════════════════════════════════════════════════════════

@app.get("/api/reservations")
def list_reservations(current_admin=Depends(get_current_admin)):
    response = supabase.table("reservations").select("*").order("created_at", desc=True).execute()
    return {"success": True, "total": len(response.data), "data": response.data}


@app.get("/api/reservations/{reservation_id}")
def get_reservation(reservation_id: str, current_admin=Depends(get_current_admin)):
    response = supabase.table("reservations").select("*").eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "data": response.data[0]}


@app.patch("/api/reservations/{reservation_id}/status")
def update_status(reservation_id: str, body: ReservationStatus, current_admin=Depends(get_current_admin)):
    valid = ["pending", "confirmed", "cancelled"]
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status tidak valid. Pilih: {', '.join(valid)}")
    response = supabase.table("reservations").update({"status": body.status}).eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "message": f"Status diubah ke '{body.status}'", "data": response.data[0]}


@app.patch("/api/reservations/{reservation_id}/notes")
def update_notes(reservation_id: str, body: AdminNotesUpdate, current_admin=Depends(get_current_admin)):
    response = supabase.table("reservations").update({"admin_notes": body.admin_notes}).eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservasi tidak ditemukan")
    return {"success": True, "message": "Catatan admin berhasil disimpan", "data": response.data[0]}
