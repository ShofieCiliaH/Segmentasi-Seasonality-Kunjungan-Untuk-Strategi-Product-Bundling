# Padusan Bundling Intelligence

Sistem ini dibuat dari proposal skripsi Anda tentang segmentasi seasonality kunjungan Wisata Padusan menggunakan Agglomerative Hierarchical Clustering untuk menentukan strategi product bundling.

Fitur utama:

- upload file transaksi `.xlsx` atau `.csv`
- cleaning data mengikuti aturan proposal
- generalisasi kategori produk menjadi `Tiket Masuk`, `Parkir`, `Wahana Air`, `Akomodasi`, dan `De Qoem (VIP)`
- normalisasi Min-Max, AHC Ward, dan rekomendasi `k` otomatis berbasis Silhouette Score
- manual override jumlah cluster
- visualisasi dendrogram dengan cut-off line
- profiling cluster dan rekomendasi paket bundling
- simpan riwayat analisis
- ekspor laporan PDF

## Akun Demo

- `stafit` / `Padusan2026!`
- `marketing` / `Padusan2026!`

## Menjalankan Aplikasi

1. Buka terminal di `D:\laragon\www\skripsi2`
2. Jalankan:

```powershell
& 'D:\laragon\bin\python\python-3.13\python.exe' app.py
```

3. Buka `http://127.0.0.1:5050`

## Menyiapkan Data Contoh

Jika ingin mencoba tanpa file riil perusahaan:

```powershell
& 'D:\laragon\bin\python\python-3.13\python.exe' scripts\generate_sample_data.py
```

File contoh akan dibuat di:

- `D:\laragon\www\skripsi2\sample_data\padusan_sample.xlsx`
- `D:\laragon\www\skripsi2\sample_data\padusan_sample.csv`

## Struktur Data Minimal

File sumber sebaiknya memiliki kolom berikut:

- `Tanggal`
- `Nama Tiket`
- `Jumlah`

Kolom tambahan seperti `Jenis Tiket` dan `Lokasi Wisata` akan dibaca jika tersedia.

## Catatan Implementasi

- Persistence prototype ini menggunakan file JSON lokal pada `D:\laragon\www\skripsi2\data\app_state.json` agar stabil di sandbox lokal. Strukturnya tetap meniru dua entitas proposal: `users` dan `riwayat_analisis`.
- Dependensi Python dipasang lokal ke folder `.vendor`.
