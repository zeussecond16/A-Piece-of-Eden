-- ═══════════════════════════════════════════════════════════════
--  A Piece of Eden — Supabase Database Schema
--  File: backend/supabase_schema.sql
--
--  CARA PAKAI:
--  1. Buka Supabase Dashboard
--  2. Klik menu "SQL Editor" di sidebar kiri
--  3. Paste seluruh isi file ini
--  4. Klik tombol "Run"
-- ═══════════════════════════════════════════════════════════════


-- ── Tabel utama untuk menyimpan data reservasi ──────────────────
CREATE TABLE IF NOT EXISTS reservations (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    
    -- Data pemesan
    name                    TEXT NOT NULL,
    email                   TEXT NOT NULL,
    phone                   TEXT NOT NULL,
    
    -- Detail acara
    event_date              DATE NOT NULL,
    time_start              TIME NOT NULL,
    time_end                TIME NOT NULL,
    guests                  INTEGER NOT NULL CHECK (guests BETWEEN 1 AND 250),
    event_description       TEXT,
    
    -- Biaya
    total_cost              BIGINT NOT NULL,   -- dalam Rupiah
    dp_amount               BIGINT NOT NULL,   -- 30% dari total_cost
    
    -- Bukti pembayaran (URL dari Supabase Storage)
    payment_proof_url       TEXT,
    payment_proof_filename  TEXT,
    
    -- Status reservasi
    status                  TEXT DEFAULT 'pending'
                            CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    
    -- Catatan admin (opsional)
    admin_notes             TEXT
);


-- ── Aktifkan Row Level Security (RLS) ───────────────────────────
-- RLS = keamanan tingkat baris. Hanya yang diizinkan yang bisa akses data.
ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;


-- ── Policy: siapa saja boleh INSERT (submit form reservasi) ──────
CREATE POLICY "Siapapun bisa submit reservasi"
    ON reservations
    FOR INSERT
    TO anon                  -- "anon" = user yang belum login
    WITH CHECK (true);


-- ── Policy: hanya admin (user login) yang bisa SELECT semua data ─
CREATE POLICY "Admin bisa lihat semua reservasi"
    ON reservations
    FOR SELECT
    TO authenticated          -- "authenticated" = user yang sudah login
    USING (true);


-- ── Policy: hanya admin yang bisa UPDATE status ──────────────────
CREATE POLICY "Admin bisa update status reservasi"
    ON reservations
    FOR UPDATE
    TO authenticated
    USING (true);


-- ── Index untuk mempercepat query berdasarkan tanggal ────────────
CREATE INDEX IF NOT EXISTS idx_reservations_event_date
    ON reservations (event_date);

CREATE INDEX IF NOT EXISTS idx_reservations_status
    ON reservations (status);

CREATE INDEX IF NOT EXISTS idx_reservations_email
    ON reservations (email);


-- ═══════════════════════════════════════════════════════════════
--  SETUP STORAGE (untuk menyimpan bukti pembayaran)
--  Jalankan ini TERPISAH di SQL Editor setelah tabel dibuat
-- ═══════════════════════════════════════════════════════════════

-- Buat bucket storage bernama "payment-proofs"
INSERT INTO storage.buckets (id, name, public)
VALUES ('payment-proofs', 'payment-proofs', false)
ON CONFLICT DO NOTHING;

-- Policy Storage: siapapun boleh upload file
CREATE POLICY "Siapapun bisa upload bukti bayar"
    ON storage.objects
    FOR INSERT
    TO anon
    WITH CHECK (bucket_id = 'payment-proofs');

-- Policy Storage: hanya admin yang bisa lihat file
CREATE POLICY "Admin bisa lihat bukti bayar"
    ON storage.objects
    FOR SELECT
    TO authenticated
    USING (bucket_id = 'payment-proofs');
