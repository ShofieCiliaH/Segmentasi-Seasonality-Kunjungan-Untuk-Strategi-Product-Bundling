# Segmentasi Seasonality Kunjungan untuk Strategi Product Bundling

Repository ini berisi implementasi prototipe sistem analitik untuk penelitian skripsi mengenai segmentasi pola kunjungan Wisata Padusan menggunakan **Agglomerative Hierarchical Clustering (AHC)** sebagai dasar penyusunan strategi **product bundling**.

Sistem dirancang untuk mengubah data transaksi historis menjadi wawasan yang dapat digunakan oleh tim internal dalam membaca pola seasonality, mengevaluasi struktur cluster, dan menghasilkan usulan paket layanan wisata secara lebih terukur.

## Ringkasan

- Domain studi: wisata pemandian air panas Padusan
- Pendekatan utama: data preprocessing, normalisasi Min-Max, Ward linkage, Euclidean distance, dan Silhouette Score
- Output utama: dendrogram, profil cluster, rekomendasi bundling, riwayat analisis, dan laporan PDF
- Bentuk aplikasi: dashboard web berbasis Flask

## Tujuan Sistem

Sistem ini dibangun untuk:

- membaca file transaksi wisata dalam format `.xlsx` atau `.csv`
- membersihkan dan mentransformasikan data transaksi ke matriks harian
- mengelompokkan pola kunjungan berdasarkan karakteristik penjualan layanan
- menyajikan rekomendasi jumlah cluster terbaik secara otomatis
- memberi ruang simulasi manual melalui override nilai `k`
- merumuskan rekomendasi product bundling berdasarkan profil cluster

## Fitur Utama

- upload data transaksi
- preprocessing sesuai aturan proposal penelitian
- generalisasi kategori produk menjadi `Tiket Masuk`, `Parkir`, `Wahana Air`, `Akomodasi`, dan `De Qoem (VIP)`
- evaluasi kandidat jumlah cluster menggunakan Silhouette Score
- visualisasi dendrogram dengan garis potong aktif
- profil cluster dan formulasi strategi bundling
- penyimpanan riwayat analisis
- ekspor laporan PDF

## Teknologi yang Digunakan

- Python 3.13
- Flask
- Pandas
- Scikit-learn
- SciPy
- Matplotlib
- OpenPyXL
- ReportLab

## Alur Analisis

1. File transaksi diunggah melalui dashboard.
2. Sistem menjalankan cleaning berdasarkan validitas tanggal, nama tiket, jumlah, dan keyword non-tiket.
3. Nama tiket digeneralisasi ke kategori layanan utama.
4. Data diubah ke matriks harian berbasis total jumlah penjualan per kategori.
5. Data dinormalisasi menggunakan Min-Max scaler.
6. AHC dengan Ward linkage dijalankan untuk membentuk cluster hari operasional.
7. Sistem menghitung Silhouette Score untuk kandidat `k`.
8. Hasil cluster diprofilkan menjadi strategi bundling yang dapat dilihat dan diunduh.

## Struktur Repository

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- CHANGELOG.md
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- REPOSITORY_STRUCTURE.md
|   `-- releases/
|       `-- v0.1.0.md
|-- sample_data/
|-- scripts/
|-- src/
|   |-- db.py
|   `-- services/
|       |-- analysis.py
|       `-- reporting.py
|-- static/
|   `-- css/
`-- templates/
```

Penjelasan lebih rinci tersedia di [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md).

## Menjalankan Aplikasi

1. Buka terminal di root project.
2. Jalankan perintah berikut:

```powershell
& 'D:\laragon\bin\python\python-3.13\python.exe' app.py
```

3. Buka `http://127.0.0.1:5050`

## Akun Demo

- `stafit` / `Padusan2026!`
- `marketing` / `Padusan2026!`

## Menjalankan Data Contoh

Jika ingin mencoba sistem tanpa data operasional riil, jalankan:

```powershell
& 'D:\laragon\bin\python\python-3.13\python.exe' scripts\generate_sample_data.py
```

File contoh akan tersedia di folder `sample_data/`.

## Spesifikasi Data Minimum

Kolom minimum yang diperlukan:

- `Tanggal`
- `Nama Tiket`
- `Jumlah`

Kolom pendukung yang akan dibaca jika tersedia:

- `Jenis Tiket`
- `Lokasi Wisata`
- `Harga`
- `Total Kotor`
- `Nominal Diskon`
- `Pendapatan`

## Kebijakan Data

- Data asli penelitian **tidak disertakan** dalam repository publik.
- File yang berpotensi sensitif, hasil analisis lokal, dan storage aplikasi diabaikan melalui `.gitignore`.
- Repository ini hanya memuat source code, sample data sintetis, dan dokumentasi.

## Dokumentasi Tambahan

- [CHANGELOG.md](CHANGELOG.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md)
- [docs/releases/v0.1.0.md](docs/releases/v0.1.0.md)

## Status Rilis

Versi repository saat ini didokumentasikan sebagai **v0.1.0** dan merepresentasikan prototipe fungsional awal untuk:

- analisis clustering
- dashboard visualisasi
- penyimpanan riwayat
- ekspor laporan

## Catatan Implementasi

- Persistence lokal menggunakan file JSON pada `data/app_state.json` untuk menjaga kestabilan prototype.
- Struktur persistence tetap meniru dua entitas proposal: `users` dan `riwayat_analisis`.
- Dependensi lokal saat pengembangan dapat dipasang ke folder `.vendor`, namun folder tersebut tidak ikut dipublikasikan.
