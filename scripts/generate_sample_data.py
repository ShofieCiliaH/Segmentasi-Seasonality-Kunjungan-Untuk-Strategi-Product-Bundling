from __future__ import annotations

import random
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VENDOR_DIR = BASE_DIR / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

import pandas as pd

OUTPUT_DIR = BASE_DIR / "sample_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rng = random.Random(42)
rows = []


def add_row(tanggal, jenis, nama_tiket, harga, jumlah):
    total = harga * jumlah
    rows.append(
        {
            "Tanggal": tanggal.strftime("%d/%m/%Y"),
            "Lokasi Wisata": "Padusan",
            "Jenis Tiket": jenis,
            "Nama Tiket": nama_tiket,
            "Harga": harga,
            "Jumlah": jumlah,
            "Total Kotor": total,
            "Nominal Diskon": 0,
            "Pendapatan": total,
        }
    )


for tanggal in pd.date_range("2025-01-01", "2025-04-30", freq="D"):
    is_weekend = tanggal.weekday() >= 5
    high_season = tanggal.month in {1, 4} and (tanggal.day <= 5 or tanggal.day >= 26)

    if high_season:
        tiket = rng.randint(900, 1500)
        parkir_r2 = rng.randint(180, 260)
        parkir_r4 = rng.randint(70, 130)
        wahana = rng.randint(550, 950)
        akomodasi = rng.randint(15, 40)
        vip = rng.randint(4, 12)
    elif is_weekend:
        tiket = rng.randint(320, 620)
        parkir_r2 = rng.randint(90, 170)
        parkir_r4 = rng.randint(30, 75)
        wahana = rng.randint(120, 260)
        akomodasi = rng.randint(55, 110)
        vip = rng.randint(2, 8)
    else:
        tiket = rng.randint(120, 260)
        parkir_r2 = rng.randint(30, 80)
        parkir_r4 = rng.randint(10, 28)
        wahana = rng.randint(45, 110)
        akomodasi = rng.randint(6, 25)
        vip = rng.randint(0, 3)

    add_row(tanggal, "KTM", "KTM Weekend Dewasa", 15500, tiket)
    add_row(tanggal, "Kendaraan", "Parkir Roda 2", 2000, parkir_r2)
    add_row(tanggal, "Kendaraan", "Parkir Roda 4", 3000, parkir_r4)
    add_row(tanggal, "Wahana", "Whirlpool Dewasa", 15000, wahana)
    add_row(tanggal, "Akomodasi", "Pinus Weekday", 70000, akomodasi)
    add_row(tanggal, "Wahana", "DQOEM2", 150000, vip)

    if tanggal.day % 17 == 0:
        add_row(tanggal, "Administratif", "Sharing Profit Mitra", 100000, 1)
    if tanggal.day % 23 == 0:
        add_row(tanggal, "KTM", "", 15000, 8)
    if tanggal.day % 29 == 0:
        add_row(tanggal, "KTM", "KTM Weekend Dewasa", 15500, 0)


frame = pd.DataFrame(rows)
frame.to_csv(OUTPUT_DIR / "padusan_sample.csv", index=False)
frame.to_excel(OUTPUT_DIR / "padusan_sample.xlsx", index=False)

print("Sample data generated:")
print((OUTPUT_DIR / "padusan_sample.csv").resolve())
print((OUTPUT_DIR / "padusan_sample.xlsx").resolve())
