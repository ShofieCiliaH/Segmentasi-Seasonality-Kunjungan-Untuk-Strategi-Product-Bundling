# Architecture Overview

Dokumen ini menjelaskan struktur logis aplikasi prototipe segmentasi seasonality kunjungan wisata.

## Layer Utama

### 1. Presentation Layer

Komponen antarmuka berada pada:

- `templates/`
- `static/css/`
- `app.py`

Lapisan ini menangani:

- login pengguna
- upload file transaksi
- tampilan dashboard hasil analisis
- tampilan riwayat analisis
- akses file laporan dan visualisasi

### 2. Application Layer

Koordinasi request dan alur utama sistem dijalankan di:

- `app.py`

Tanggung jawab utama:

- routing Flask
- sesi login
- pengelolaan upload
- eksekusi pipeline analitik
- penyimpanan hasil ke persistence lokal

### 3. Analysis Layer

Modul inti analisis ada di:

- `src/services/analysis.py`

Tanggung jawab utama:

- normalisasi header
- parsing numerik
- filtering data tidak valid
- kategorisasi produk
- transformasi data ke matriks harian
- normalisasi Min-Max
- perhitungan linkage matrix
- evaluasi Silhouette Score
- profiling cluster
- formulasi rule-based bundling

### 4. Reporting Layer

Pembuatan output dokumen formal dilakukan oleh:

- `src/services/reporting.py`

Output:

- PDF laporan analisis
- ringkasan hasil cluster
- tabel strategi rekomendasi

### 5. Persistence Layer

Penyimpanan lokal dikelola di:

- `src/db.py`

Implementasi saat ini:

- file JSON lokal untuk `users`
- file JSON lokal untuk `riwayat_analisis`

Catatan:

- pada proposal, persistence diarahkan ke DBMS
- pada prototype publik ini, pendekatan JSON dipakai untuk menjaga portabilitas dan kesederhanaan setup
