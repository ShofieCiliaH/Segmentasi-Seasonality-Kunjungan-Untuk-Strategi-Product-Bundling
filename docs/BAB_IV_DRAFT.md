# BAB IV

# HASIL DAN PEMBAHASAN

Bab ini memaparkan hasil penelitian sesuai alur kerja yang telah dirancang pada Bab III, yaitu dimulai dari pengumpulan data, pra-pemrosesan data, proses clustering, evaluasi dan validasi model, perancangan rekomendasi strategi product bundling, implementasi sistem, pengujian sistem, hingga pembahasan hasil. Dengan susunan tersebut, Bab IV tidak hanya menampilkan luaran akhir analisis, tetapi juga menjelaskan bagaimana setiap tahapan metode diimplementasikan pada sistem yang dibangun.

## 4.1 Pengumpulan Data

Tahap pengumpulan data pada penelitian ini menggunakan data sekunder berupa rekam transaksi penjualan tiket Wisata Padusan periode 1 Januari 2022 sampai dengan 30 November 2025. Data disediakan dalam empat file tahunan, yaitu `2022.xlsx`, `2023.xlsx`, `2024.xlsx`, dan `2025.xlsx`. Secara implementatif, proses pembacaan data pada sistem dijalankan melalui fungsi `analyze()` pada file `app.py`, kemudian berkas diproses oleh fungsi `load_dataset()` pada file `analysis.py`. Fungsi ini dirancang untuk membaca file berformat `.xlsx` maupun `.csv`, sehingga proses input data pada sistem tetap fleksibel.

Berdasarkan hasil penggabungan seluruh file tahunan, diperoleh 13.586 baris transaksi dengan 1.427 hari operasional unik. Ringkasan dataset penelitian disajikan pada Tabel 4.1.

**Caption Tabel 4.1. Ringkasan dataset penelitian**

| Komponen | Nilai |
|---|---|
| Periode data | 1 Januari 2022 - 30 November 2025 |
| Jumlah file sumber | 4 file tahunan |
| Nama file sumber | 2022.xlsx, 2023.xlsx, 2024.xlsx, 2025.xlsx |
| Jumlah baris awal | 13.586 |
| Jumlah hari operasional unik | 1.427 |

Secara implementatif, proses pembacaan data dimulai dengan memanggil fungsi `load_dataset()`, lalu sistem memetakan nama kolom yang relevan dan membentuk `working_df` sebagai dataframe kerja. Potongan kode yang merepresentasikan proses tersebut ditunjukkan pada Gambar 4.1.

**Caption Gambar 4.1. Potongan kode pembacaan data transaksi**

```python
raw_df = load_dataset(source_path)
column_map = resolve_columns(raw_df)
working_df = pd.DataFrame(
    {
        "tanggal": raw_df[column_map["tanggal"]],
        "nama_tiket": raw_df[column_map["nama_tiket"]],
        "jumlah": raw_df[column_map["jumlah"]],
        "jenis_tiket": raw_df[column_map["jenis_tiket"]] if "jenis_tiket" in column_map else "",
        "lokasi_wisata": raw_df[column_map["lokasi_wisata"]] if "lokasi_wisata" in column_map else "",
    }
)
```

Potongan kode pada Gambar 4.1 menunjukkan bahwa sistem tidak langsung memproses seluruh kolom dari file mentah, melainkan terlebih dahulu mengekstrak atribut yang dibutuhkan untuk tahapan analisis berikutnya.

Sebelum memasuki tahap pra-pemrosesan, sistem terlebih dahulu mengenali atribut yang relevan dari file transaksi. Identifikasi nama kolom dilakukan oleh fungsi `resolve_columns()` pada file `analysis.py`, sehingga variasi penamaan header pada file Excel masih dapat ditangani selama tetap merujuk pada kolom inti yang dibutuhkan. Atribut mentah utama yang dimanfaatkan sistem ditunjukkan pada Tabel 4.2.

**Caption Tabel 4.2. Atribut utama data transaksi yang dimanfaatkan sistem**

| Atribut Mentah | Fungsi dalam Sistem | Keterangan |
|---|---|---|
| `tanggal` | Penanda waktu operasional | Digunakan untuk membentuk unit analisis berbasis hari |
| `nama_tiket` | Identifikasi produk | Digunakan untuk generalisasi kategori layanan |
| `jumlah` | Nilai quantity transaksi | Menjadi dasar perhitungan intensitas permintaan |
| `jenis_tiket` | Atribut pendukung kategorisasi | Membantu pemetaan produk pada kondisi nama tiket ambigu |
| `lokasi_wisata` | Konteks sumber transaksi | Dipertahankan sebagai atribut pendukung saat pembacaan data |

Selain ringkasan struktur data, distribusi volume transaksi per tahun juga penting untuk menunjukkan skala operasional historis. Rekapitulasi total quantity berdasarkan kategori utama hasil generalisasi ditampilkan pada Tabel 4.3.

**Caption Tabel 4.3. Rekap total quantity per tahun berdasarkan kategori utama**

| Tahun | Akomodasi | De Qoem (VIP) | Parkir | Tiket Masuk | Wahana Air |
|---|---:|---:|---:|---:|---:|
| 2022 | 277 | 2.038 | 44.550 | 148.220 | 111.076 |
| 2023 | 16 | 3.149 | 123.814 | 375.236 | 313.313 |
| 2024 | 6 | 3.546 | 147.082 | 384.214 | 403.746 |
| 2025 | 5 | 2.950 | 129.975 | 316.828 | 352.928 |

Berdasarkan Tabel 4.3 dapat diketahui bahwa kategori dengan volume tertinggi secara umum berada pada layanan Tiket Masuk dan Wahana Air. Tahun 2024 menjadi periode dengan total quantity tertinggi pada kedua kategori tersebut. Kondisi ini menunjukkan bahwa pola permintaan utama pengunjung lebih banyak terkonsentrasi pada kunjungan reguler dan penggunaan fasilitas wahana air.

## 4.2 Pra-pemrosesan Data

Tahap pra-pemrosesan data dilakukan untuk mengubah data mentah menjadi format yang bersih, konsisten, dan siap dianalisis oleh algoritma clustering. Dalam implementasi sistem, seluruh tahapan ini dijalankan secara terpusat di fungsi `run_analysis()` pada file `analysis.py`, dengan dukungan fungsi `resolve_columns()`, `parse_numeric()`, `categorize_product()`, `serialize_frame()`, dan `compute_outlier_summary()`.

### 4.2.1 Pembersihan Data

Langkah pertama pada pra-pemrosesan adalah pembersihan data. Tahap ini mencakup validasi tanggal, validasi nilai jumlah, penghapusan nama tiket kosong, penghapusan transaksi dengan jumlah nol atau negatif, serta penyaringan kata kunci non-tiket seperti `sharing`, `fix`, `mitra`, dan `sewa` yang tidak merepresentasikan perilaku pembelian pengunjung. Secara implementatif, validasi nama kolom dilakukan dengan `resolve_columns()`, sedangkan konversi nilai numerik ditangani oleh `parse_numeric()`. Proses penyaringan utama dilakukan langsung di dalam `run_analysis()`.

Ringkasan hasil pembersihan data ditampilkan pada Tabel 4.4.

**Caption Tabel 4.4. Hasil pembersihan data transaksi**

| Jenis pembersihan | Jumlah baris |
|---|---:|
| Tanggal tidak valid | 43 |
| Nama tiket kosong | 0 |
| Nilai jumlah kosong | 66 |
| Jumlah bernilai 0 | 100 |
| Jumlah bernilai negatif | 0 |
| Data non-tiket/keyword tidak relevan | 56 |
| Data tidak terkategori | 65 |
| Total baris valid | 13.256 |

Di dalam implementasinya, tahapan pembersihan dilakukan secara berurutan, dimulai dari konversi tipe data hingga penyaringan baris yang tidak layak analisis. Ringkasan potongan kode yang mewakili proses tersebut ditunjukkan pada Gambar 4.2.

**Caption Gambar 4.2. Potongan kode pembersihan data transaksi**

```python
working_df["tanggal"] = pd.to_datetime(working_df["tanggal"], dayfirst=True, errors="coerce")
working_df["jumlah"] = working_df["jumlah"].apply(parse_numeric)

cleaned_df = working_df.copy()
cleaned_df = cleaned_df[~cleaned_df["tanggal"].isna()]
cleaned_df = cleaned_df[~cleaned_df["nama_tiket"].isin({"", "nan", "None"})]
cleaned_df = cleaned_df[~cleaned_df["jumlah"].isna()]
cleaned_df = cleaned_df[cleaned_df["jumlah"] > 0]
```

Potongan kode tersebut memperlihatkan bahwa pembersihan data dilakukan dengan pendekatan filtering bertahap. Cara ini memudahkan sistem menghitung jumlah baris yang tereliminasi pada setiap aturan pembersihan.

Berdasarkan Tabel 4.4 dapat diketahui bahwa dari total 13.586 baris transaksi awal, sebanyak 330 baris tidak dapat digunakan dalam analisis utama. Meskipun demikian, sebanyak 13.256 baris tetap dinyatakan valid sehingga basis data historis yang dianalisis masih sangat memadai untuk proses clustering.

### 4.2.2 Seleksi Fitur

Setelah data bersih, sistem melakukan seleksi atribut yang relevan untuk analisis. Pada tahap ini, tidak seluruh kolom transaksi mentah digunakan secara langsung. Sistem membentuk `working_df` di dalam `run_analysis()` yang berfokus pada atribut inti, yaitu `tanggal`, `nama_tiket`, `jumlah`, `jenis_tiket`, dan `lokasi_wisata`. Pemilihan ini dilakukan karena lima atribut tersebut telah mencukupi kebutuhan untuk membentuk pola kunjungan harian dan pemetaan kategori produk.

Rincian atribut hasil seleksi ditunjukkan pada Tabel 4.5.

**Caption Tabel 4.5. Atribut hasil seleksi fitur pada tahap pra-pemrosesan**

| Atribut | Status Penggunaan | Peran dalam Analisis |
|---|---|---|
| `tanggal` | Digunakan | Membentuk unit analisis per hari operasional |
| `nama_tiket` | Digunakan | Menjadi dasar pemetaan kategori produk |
| `jumlah` | Digunakan | Menjadi nilai quantity untuk agregasi harian |
| `jenis_tiket` | Digunakan | Membantu proses generalisasi kategori |
| `lokasi_wisata` | Digunakan sebagai pendukung | Menjaga konteks sumber transaksi |

Dengan seleksi atribut tersebut, sistem tidak lagi bergantung pada kolom nominal, pendapatan, atau diskon. Pendekatan ini selaras dengan batasan penelitian yang memang memfokuskan analisis pada quantity transaksi sebagai representasi intensitas permintaan pengunjung.

Contoh potongan implementasi seleksi fitur pada sistem dapat dituliskan sebagai berikut.

```python
working_df = raw_df[
    [date_col, name_col, quantity_col, kind_col, location_col]
].copy()
working_df.columns = [
    "tanggal",
    "nama_tiket",
    "jumlah",
    "jenis_tiket",
    "lokasi_wisata",
]
```

Potongan kode tersebut menunjukkan bahwa seleksi fitur pada penelitian ini dilakukan secara eksplisit dengan mengambil kolom yang memang dibutuhkan oleh pipeline analisis. Dengan pendekatan tersebut, struktur data kerja menjadi lebih ringkas dan lebih mudah dikendalikan pada tahap-tahap berikutnya.

### 4.2.3 Generalisasi dan Pemetaan Kategori Produk

Langkah berikutnya adalah generalisasi nama layanan ke dalam kategori utama. Tahap ini diimplementasikan melalui fungsi `categorize_product()` pada file `analysis.py`. Fungsi tersebut membaca `nama_tiket` dan `jenis_tiket`, kemudian memetakan setiap transaksi ke lima kategori utama, yaitu `Tiket Masuk`, `Parkir`, `Wahana Air`, `Akomodasi`, dan `De Qoem (VIP)`.

Skema generalisasi yang digunakan sistem ditunjukkan pada Tabel 4.6.

**Caption Tabel 4.6. Skema generalisasi dan pemetaan kategori produk**

| Kategori Utama | Kata kunci/indikator utama pada sistem |
|---|---|
| Akomodasi | `camp`, `cabin`, `glamping`, `pinus`, `flamboyan`, `penginapan`, `resort`, `onsen`, `stay`, `bobocabin`, `soemo`, `jungle` |
| De Qoem (VIP) | `dqoem`, `de qoem`, `d'qoem`, `dqom` |
| Parkir | `parkir`, `roda 2`, `roda 4`, `roda 6`, `r2`, `r4`, `r6`, atau jenis tiket kendaraan |
| Tiket Masuk | `tiket masuk`, `ktm`, `weekend`, `weekday`, `dewasa`, `anak`, `reguler` |
| Wahana Air | `whirlpool`, `kolam`, `gambiran`, `air panas`, `therapy`, `terapi`, atau jenis tiket wahana |

Pada level implementasi, proses generalisasi dilakukan dengan memanggil fungsi `categorize_product()` untuk setiap baris transaksi. Fungsi ini membaca kombinasi `nama_tiket` dan `jenis_tiket`, lalu mengembalikan label kategori utama. Potongan kode sederhananya ditunjukkan pada Gambar 4.3.

**Caption Gambar 4.3. Potongan kode generalisasi kategori produk**

```python
cleaned_df["kategori_produk"] = cleaned_df.apply(
    lambda row: categorize_product(row["nama_tiket"], row["jenis_tiket"]),
    axis=1,
)

filtered_df = cleaned_df[cleaned_df["kategori_produk"] != "Lainnya"].copy()
```

Melalui mekanisme tersebut, sistem dapat mengubah nama produk yang beragam menjadi kategori yang lebih stabil untuk kebutuhan analisis. Baris yang tetap berlabel `Lainnya` kemudian dikeluarkan agar tidak menambah noise pada pembentukan cluster.

Hasil generalisasi ini sangat penting karena algoritma tidak lagi bekerja pada nama produk mentah yang sangat beragam, tetapi pada kategori layanan yang lebih stabil dan dapat dibandingkan antar-hari. Pada tahap ini, sebanyak 65 baris yang tidak dapat dipetakan ke kategori utama dikeluarkan dari analisis agar tidak menambah noise pada proses clustering.

### 4.2.4 Transformasi Matriks Harian

Setelah kategorisasi selesai, data transaksi diubah menjadi matriks harian melalui proses `groupby` dan `pivot` di dalam `run_analysis()`. Pada struktur ini, setiap baris merepresentasikan satu hari operasional, sedangkan setiap kolom merepresentasikan total quantity dari kategori utama. Hasil transformasi inilah yang menjadi input utama bagi proses clustering.

Untuk kebutuhan tampilan dashboard, sistem menampilkan cuplikan matriks melalui fungsi `serialize_frame()`. Perlu dicatat bahwa panel `Preview Matriks Harian` di aplikasi hanya menampilkan 10 baris pertama sebagai preview, sedangkan seluruh 1.427 hari operasional tetap digunakan dalam proses clustering. Contoh lima baris pertama matriks harian ditunjukkan pada Tabel 4.7.

**Caption Tabel 4.7. Contoh lima baris pertama matriks harian hasil agregasi**

| Tanggal | Akomodasi | De Qoem (VIP) | Parkir | Tiket Masuk | Wahana Air |
|---|---:|---:|---:|---:|---:|
| 2022-01-01 | 6 | 16 | 1.148 | 3.522 | 181 |
| 2022-01-02 | 4 | 15 | 1.305 | 4.082 | 215 |
| 2022-01-03 | 0 | 5 | 353 | 1.056 | 77 |
| 2022-01-04 | 0 | 5 | 200 | 587 | 125 |
| 2022-01-05 | 0 | 4 | 202 | 632 | 94 |

Secara teknis, transformasi ini dilakukan dengan operasi `groupby`, `sum`, dan `unstack`, sehingga transaksi harian pada kategori yang sama dijumlahkan terlebih dahulu sebelum diputar ke bentuk matriks. Potongan kode yang mewakili tahapan tersebut disajikan pada Gambar 4.4.

**Caption Gambar 4.4. Potongan kode pembentukan matriks harian**

```python
daily_matrix = (
    filtered_df.groupby(["tanggal", "kategori_produk"])["jumlah"]
    .sum()
    .unstack(fill_value=0)
    .sort_index()
)

for category in PRIMARY_CATEGORIES:
    if category not in daily_matrix.columns:
        daily_matrix[category] = 0
```

Potongan kode ini menunjukkan bahwa seluruh kategori utama dipastikan tersedia sebagai kolom matriks, meskipun pada hari tertentu tidak ada transaksi untuk kategori tersebut.

Berdasarkan Tabel 4.7 dapat diketahui bahwa sistem telah berhasil mereduksi data transaksi detail menjadi format time-series harian yang lebih ringkas. Bentuk matriks ini sesuai dengan rancangan Bab III karena unit analisis penelitian memang diarahkan pada pola kunjungan per hari operasional, bukan per baris transaksi mentah.

### 4.2.5 Normalisasi Data

Sebelum diproses oleh algoritma clustering, matriks harian dinormalisasi menggunakan `MinMaxScaler` di dalam `run_analysis()`. Tujuan normalisasi adalah menyetarakan rentang nilai seluruh kategori ke skala 0 sampai 1, sehingga kategori dengan volume besar seperti `Tiket Masuk` dan `Parkir` tidak secara otomatis mendominasi perhitungan jarak.

Hasil normalisasi tidak ditampilkan seluruhnya pada laporan ini karena jumlah observasi mencapai 1.427 hari. Namun secara sistem, seluruh kategori utama telah berada pada skala yang sebanding dan siap digunakan pada pengukuran jarak Euclidean. Dengan demikian, proses clustering berikutnya bekerja pada data yang telah terstandarisasi.

Implementasi normalisasi pada sistem dilakukan setelah matriks harian final terbentuk. Potongan kode yang digunakan cukup ringkas karena memanfaatkan `MinMaxScaler` dari `scikit-learn`, seperti terlihat berikut ini.

```python
scaler = MinMaxScaler()
normalized_values = scaler.fit_transform(daily_matrix.values)
normalized_matrix = pd.DataFrame(
    normalized_values,
    index=daily_matrix.index,
    columns=daily_matrix.columns,
)
```

Potongan kode di atas menegaskan bahwa proses normalisasi diterapkan pada seluruh kolom kategori secara seragam. Hasil akhirnya berupa `normalized_matrix` yang kemudian dipakai pada tahap evaluasi kandidat cluster dan pembentukan cluster final.

### 4.2.6 Pemantauan Outlier

Tahap akhir pada pra-pemrosesan adalah pemantauan outlier. Pada sistem, proses ini diimplementasikan melalui fungsi `compute_outlier_summary()` yang menggunakan pendekatan Interquartile Range (IQR). Tujuan tahap ini bukan untuk menghapus lonjakan transaksi secara otomatis, melainkan untuk mengidentifikasi tanggal-tanggal yang berada di luar rentang normal masing-masing kategori.

Sesuai rancangan metodologi pada Bab III, outlier pada penelitian ini diperlakukan sebagai `legitimate spikes`, artinya lonjakan tersebut tetap dipertahankan apabila masih masuk akal secara logika bisnis wisata. Ringkasan hasil monitoring outlier disajikan pada Tabel 4.8.

**Caption Tabel 4.8. Ringkasan hasil monitoring outlier berbasis IQR**

| Kategori | Jumlah Outlier | Contoh Tanggal dan Nilai |
|---|---:|---|
| Akomodasi | 94 | 2022-01-01: 6, 2022-01-02: 4, 2022-01-07: 2 |
| De Qoem (VIP) | 7 | 2023-02-27: 65, 2023-12-24: 31, 2023-12-25: 37 |
| Parkir | 142 | 2022-01-01: 1.148, 2022-01-02: 1.305, 2022-01-16: 875 |
| Tiket Masuk | 155 | 2022-01-01: 3.522, 2022-01-02: 4.082, 2022-01-09: 2.780 |
| Wahana Air | 122 | 2022-05-05: 2.866, 2022-05-07: 2.846, 2022-05-08: 2.742 |

Pada sisi implementasi, perhitungan outlier diringkas ke dalam fungsi `compute_outlier_summary()`. Meskipun fungsi lengkapnya melakukan iterasi untuk setiap kategori, ringkasan alur Python-nya dapat dituliskan seperti pada Gambar 4.5.

**Caption Gambar 4.5. Potongan kode monitoring outlier berbasis IQR**

```python
for column in matrix.columns:
    series = matrix[column]
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_fence = q1 - (1.5 * iqr)
    upper_fence = q3 + (1.5 * iqr)
```

Potongan kode ini memperlihatkan bahwa sistem menghitung pagar bawah dan pagar atas IQR untuk setiap kategori, lalu menandai tanggal yang berada di luar rentang tersebut sebagai outlier monitoring.

Berdasarkan Tabel 4.8 dapat diketahui bahwa kategori `Tiket Masuk`, `Parkir`, dan `Wahana Air` memiliki jumlah lonjakan paling banyak. Temuan ini wajar karena tiga kategori tersebut memang menjadi layanan utama Wisata Padusan. Oleh sebab itu, hasil monitoring outlier diposisikan sebagai bahan interpretasi, bukan sebagai dasar eliminasi data secara otomatis.

## 4.3 Proses Clustering

Tahap inti penelitian adalah penerapan algoritma Agglomerative Hierarchical Clustering (AHC). Pada sistem, proses ini dijalankan melalui fungsi `cluster_and_profile()` di file `analysis.py`. Fungsi tersebut bekerja pada matriks harian yang telah dinormalisasi, lalu membentuk kelompok hari operasional berdasarkan tingkat kemiripan pola permintaannya.

### 4.3.1 Pengukuran Jarak dan Kriteria Penggabungan

Sesuai rancangan Bab III, pengukuran kemiripan antar-hari pada penelitian ini menggunakan Euclidean Distance, sedangkan kriteria penggabungan cluster menggunakan metode Ward. Implementasi teknisnya terlihat pada pemanggilan `linkage(normalized_matrix.values, method="ward")` di dalam `cluster_and_profile()`. Pendekatan ini dipilih karena metode Ward berupaya meminimalkan kenaikan varians intra-cluster pada setiap tahap penggabungan, sehingga kelompok yang terbentuk cenderung lebih kompak.

Dengan penggunaan Euclidean Distance pada data yang telah dinormalisasi, sistem dapat membandingkan pola permintaan lima kategori utama secara seimbang. Selanjutnya, metode Ward menyusun proses penggabungan secara bertahap dari objek paling mirip hingga terbentuk struktur hierarkis secara lengkap.

### 4.3.2 Pembentukan Struktur Hierarki dan Dendrogram

Hasil dari proses AHC divisualisasikan dalam bentuk dendrogram melalui fungsi `render_dendrogram()` pada file `analysis.py`. Visualisasi ini penting karena membantu peneliti melihat hubungan hierarkis antar-hari operasional sebelum dilakukan pemotongan cluster.

**Caption Gambar 4.6. Dendrogram hasil Agglomerative Hierarchical Clustering pada data asli periode 2022-2025**

Gunakan gambar:

`D:\laragon\www\skripsi2\storage\generated\plots\dendrogram-data-asli-2022-2025.png`

Narasi setelah gambar:

Gambar 4.6 menunjukkan struktur penggabungan hari operasional berdasarkan kemiripan pola penjualan. Perlu diperhatikan bahwa urutan tanggal pada sumbu horizontal dendrogram tidak merepresentasikan urutan waktu secara kronologis, melainkan urutan objek berdasarkan kedekatan hasil pengelompokan. Dengan demikian, tanggal yang letaknya berdekatan pada dendrogram adalah tanggal yang secara pola transaksinya dianggap lebih mirip oleh algoritma.

## 4.4 Evaluasi dan Validasi Model

Setelah struktur hierarki terbentuk, tahap berikutnya adalah menentukan jumlah cluster terbaik, memvalidasi kualitas hasil pengelompokan, dan membentuk profil masing-masing cluster. Tahapan ini diimplementasikan melalui fungsi `evaluate_candidates()` dan `cluster_and_profile()` pada file `analysis.py`.

### 4.4.1 Penentuan Jumlah Cluster

Pada sistem, jumlah cluster tidak ditetapkan sejak awal secara manual, melainkan dicari secara otomatis dengan menguji beberapa kandidat nilai `k`. Implementasi ini dilakukan oleh fungsi `evaluate_candidates()` yang menghitung `Silhouette Score` untuk `k = 2` sampai `k = 6`. Hasil evaluasi kandidat cluster ditunjukkan pada Tabel 4.9.

**Caption Tabel 4.9. Hasil evaluasi jumlah cluster menggunakan Silhouette Score**

| Nilai k | Silhouette Score |
|---:|---:|
| 2 | 0,6128 |
| 3 | 0,6335 |
| 4 | 0,4640 |
| 5 | 0,4681 |
| 6 | 0,4704 |

Berdasarkan Tabel 4.9 dapat diketahui bahwa nilai Silhouette Score tertinggi diperoleh pada `k = 3`, yaitu sebesar `0,6335`. Oleh karena itu, jumlah cluster yang digunakan dalam analisis utama penelitian ini adalah tiga cluster. Pemilihan ini bersifat data-driven dan konsisten dengan rancangan evaluasi otomatis pada Bab III.

Di tingkat implementasi, evaluasi kandidat cluster dilakukan dengan iterasi nilai `k` dan penghitungan `silhouette_score` pada masing-masing kandidat. Potongan kode yang mewakili tahap ini ditunjukkan pada Gambar 4.7.

**Caption Gambar 4.7. Potongan kode evaluasi kandidat jumlah cluster**

```python
for cluster_count in range(2, max_clusters + 1):
    labels = fcluster(full_linkage, t=cluster_count, criterion="maxclust")
    score = round(float(silhouette_score(normalized_matrix.values, labels)), 4)
    scores.append({"k": cluster_count, "score": score})

recommended = max(scores, key=lambda item: item["score"])["k"]
```

Potongan kode tersebut menunjukkan bahwa jumlah cluster optimal ditentukan berdasarkan skor siluet tertinggi, bukan berdasarkan asumsi peneliti sejak awal.

### 4.4.2 Validasi Kualitas Cluster dan Profiling

Setelah nilai `k` terbaik diperoleh, sistem menjalankan fungsi `cluster_and_profile()` untuk membentuk cluster final, menghitung jumlah hari per cluster, proporsi akhir pekan, rentang tanggal, serta nilai centroid setiap kategori. Hasil ringkasan cluster ditampilkan pada Tabel 4.10.

**Caption Tabel 4.10. Ringkasan hasil cluster pada data asli**

| Cluster | Jumlah Hari | Proporsi Akhir Pekan | Label Sistem | Paket Rekomendasi |
|---|---:|---:|---|---|
| Cluster 1 | 336 | 75,6% | Low Season / Weekday | Paket Hemat Weekday |
| Cluster 2 | 30 | 73,3% | Staycation / Weekend Pattern | Paket Camping Adventure |
| Cluster 3 | 1.061 | 12,6% | Low Season / Weekday | Paket Hemat Weekday |

Untuk memahami karakter masing-masing cluster secara numerik, sistem menghitung centroid pada lima kategori utama. Nilai centroid tersebut disajikan pada Tabel 4.11.

**Caption Tabel 4.11. Nilai centroid cluster hasil analisis**

| Cluster | Tiket Masuk | Parkir | Wahana Air | Akomodasi | De Qoem (VIP) |
|---|---:|---:|---:|---:|---:|
| Cluster 1 | 0,0953 | 0,0801 | 0,0871 | 0,0074 | 0,2833 |
| Cluster 2 | 0,1023 | 0,0714 | 0,0610 | 0,5722 | 0,1764 |
| Cluster 3 | 0,0151 | 0,0143 | 0,0196 | 0,0053 | 0,0747 |

Berdasarkan Tabel 4.11 dapat diketahui bahwa Cluster 2 memiliki dominasi pada kategori `Akomodasi`, sedangkan Cluster 1 dan Cluster 3 memperlihatkan nilai yang relatif rendah pada hampir seluruh kategori utama. Informasi centroid inilah yang kemudian dibaca oleh fungsi `infer_segment()` untuk memberi label segmen dan rekomendasi strategi bundling. Pada sisi implementasi, pembentukan cluster final dilakukan dengan memotong hasil `linkage` menggunakan `fcluster`, kemudian sistem membentuk dataframe assignment untuk menghitung centroid, proporsi akhir pekan, dan profil masing-masing cluster. Ringkasan potongan kodenya ditunjukkan pada Gambar 4.8.

**Caption Gambar 4.8. Potongan kode pembentukan cluster dan profiling**

```python
labels = fcluster(
    linkage(normalized_matrix.values, method="ward"),
    t=cluster_count,
    criterion="maxclust",
).tolist()

assignments = pd.DataFrame({"cluster": labels}, index=raw_matrix.index)
combined = normalized_matrix.join(assignments)
```

Potongan kode ini menggambarkan tahap awal pembentukan cluster final, yaitu menetapkan label cluster pada setiap hari operasional sebelum proses profiling dilakukan lebih lanjut.

### 4.4.3 Interpretasi Hasil Profil Cluster

Interpretasi cluster dilakukan dengan menggabungkan informasi `day_count`, `weekend_share`, `centroid`, dan `profile_text` yang dibentuk sistem. Secara rinci, hasil interpretasi tiap cluster adalah sebagai berikut.

**1. Cluster 1**

Cluster 1 terdiri dari 336 hari operasional. Proporsi akhir pekan pada cluster ini mencapai 75,6%, tetapi nilai centroid kategori utama masih relatif rendah. Secara sistem, cluster ini diberi label `Low Season / Weekday` dengan rekomendasi `Paket Hemat Weekday`. Kondisi ini menunjukkan bahwa keberadaan hari akhir pekan tidak selalu identik dengan lonjakan permintaan tinggi pada seluruh layanan.

**2. Cluster 2**

Cluster 2 terdiri dari 30 hari operasional dan memiliki proporsi akhir pekan sebesar 73,3%. Ciri paling kuat dari cluster ini adalah nilai centroid `Akomodasi` sebesar 0,5722, yang jauh lebih tinggi dibanding cluster lain. Oleh karena itu, sistem mengidentifikasinya sebagai `Staycation / Weekend Pattern` dan merekomendasikan `Paket Camping Adventure`.

**3. Cluster 3**

Cluster 3 merupakan cluster terbesar dengan 1.061 hari operasional. Proporsi akhir pekan pada cluster ini hanya 12,6%, sehingga lebih banyak berisi hari kerja biasa. Nilai centroid pada seluruh kategori utama juga merupakan yang paling rendah. Karena itu, sistem memberi label `Low Season / Weekday` dan rekomendasi `Paket Hemat Weekday`.

## 4.5 Perancangan Rekomendasi Strategi Product Bundling

Tahap berikutnya adalah menerjemahkan hasil segmentasi ke dalam strategi product bundling. Pada sistem, proses ini diimplementasikan melalui fungsi `infer_segment()` dan `get_segment_descriptions()` pada file `analysis.py`. Fungsi `infer_segment()` bertugas menentukan label segmen, nama paket, komponen paket, dan target waktu berdasarkan nilai centroid serta proporsi akhir pekan. Selanjutnya, `get_segment_descriptions()` membentuk penjelasan otomatis mengenai alasan rekomendasi.

Hasil rekomendasi strategi bundling pada data asli dirangkum pada Tabel 4.12.

**Caption Tabel 4.12. Rekomendasi strategi product bundling berdasarkan hasil clustering**

| Cluster | Label Sistem | Strategi Bundling | Komposisi |
|---|---|---|---|
| Cluster 1 | Low Season / Weekday | Paket Hemat Weekday | Tiket Masuk + Parkir |
| Cluster 2 | Staycation / Weekend Pattern | Paket Camping Adventure | Tiket Masuk + Akomodasi |
| Cluster 3 | Low Season / Weekday | Paket Hemat Weekday | Tiket Masuk + Parkir |

Berdasarkan Tabel 4.12 dapat diketahui bahwa strategi `Paket Hemat Weekday` muncul sebagai rekomendasi dominan karena dua dari tiga cluster memiliki karakteristik permintaan relatif rendah. Sementara itu, `Paket Camping Adventure` muncul pada cluster yang memperlihatkan dominasi permintaan akomodasi. Dengan demikian, sistem tidak memaksakan munculnya paket high season, tetapi menyesuaikan rekomendasi dengan karakter data historis yang benar-benar terbentuk.

Untuk memperjelas alasan sistem dalam memilih strategi tersebut, deskripsi otomatis yang dihasilkan pada aplikasi dapat dijelaskan sebagai berikut.

- Cluster 1 direkomendasikan menggunakan `Paket Hemat Weekday` karena pola permintaannya rendah pada kategori utama dan lebih sesuai ditangani dengan bundling sederhana.
- Cluster 2 direkomendasikan menggunakan `Paket Camping Adventure` karena cluster ini menunjukkan dominasi layanan akomodasi dan kecenderungan aktivitas akhir pekan.
- Cluster 3 kembali diarahkan ke `Paket Hemat Weekday` karena merupakan kelompok hari operasional dengan intensitas permintaan paling rendah dan paling dominan jumlahnya.

Rule generation pada penelitian ini tidak dibuat dalam bentuk aturan verbal semata, tetapi ditanamkan langsung pada fungsi `infer_segment()`. Fungsi tersebut membaca nilai centroid dan `weekend_share`, kemudian mengembalikan label segmen beserta nama paket bundling. Potongan kode yang mewakili logika tersebut ditunjukkan pada Gambar 4.9.

**Caption Gambar 4.9. Potongan kode rule generation strategi bundling**

```python
if tiket > 0.55 and parkir > 0.45 and wahana > 0.55:
    return "High Season / Peak Days", "Paket Terusan Wahana Air", ...

if akomodasi > 0.55 or (akomodasi > 0.4 and weekend_share >= 0.55):
    return "Staycation / Weekend Pattern", "Paket Camping Adventure", ...

if overall <= 0.35:
    return "Low Season / Weekday", "Paket Hemat Weekday", ...
```

Potongan kode pada Gambar 4.9 menunjukkan bahwa strategi bundling dibentuk secara rule-based berdasarkan profil cluster, sehingga rekomendasi yang keluar tetap konsisten dengan karakter data historis yang dianalisis.

## 4.6 Hasil Implementasi Sistem

Setelah model analitik selesai dibangun, penelitian ini mengimplementasikan seluruh alur analisis ke dalam bentuk aplikasi berbasis web. Orkestrasi antarmuka dan alur pengguna ditangani oleh file `app.py`, sedangkan tampilan dibentuk menggunakan template HTML pada folder `templates` dan stylesheet pada file `app.css`. Fitur pelaporan PDF diimplementasikan melalui fungsi `generate_report_pdf()` pada file `reporting.py`.

Secara fungsional, sistem mendukung proses login, unggah file data transaksi, eksekusi analisis clustering, visualisasi dendrogram, penyimpanan riwayat analisis, pembukaan detail hasil, dan ekspor laporan PDF. Hal ini menunjukkan bahwa penelitian tidak berhenti pada perhitungan algoritmik, tetapi berhasil diwujudkan menjadi perangkat lunak yang dapat digunakan langsung.

**Caption Gambar 4.10. Tampilan dashboard utama sistem analisis**

Saran gambar:

Gunakan screenshot halaman dashboard utama setelah pengguna login dan sebelum atau sesudah analisis dijalankan.

**Caption Gambar 4.11. Tampilan halaman riwayat dan detail hasil analisis**

Saran gambar:

Gunakan screenshot halaman riwayat analisis atau halaman detail hasil untuk menunjukkan bahwa metadata hasil analisis disimpan dan dapat dipanggil kembali.

**Caption Gambar 4.12. Tampilan laporan PDF hasil analisis**

Saran gambar:

Gunakan screenshot file PDF hasil analisis dari aplikasi.

Narasi setelah gambar:

Implementasi sistem memperlihatkan bahwa tahapan yang dirancang pada Bab III, mulai dari input data, pra-pemrosesan, clustering, evaluasi, pembentukan rekomendasi, hingga penyajian hasil, telah dapat diwujudkan dalam satu dashboard terintegrasi. Dengan demikian, penelitian ini menghasilkan artefak perangkat lunak yang fungsional sekaligus mendukung proses pengambilan keputusan berbasis data.

## 4.7 Hasil Pengujian Sistem

Pengujian sistem pada penelitian ini dilakukan untuk mengetahui apakah sistem yang dibangun telah berfungsi sesuai kebutuhan dan dapat diterima oleh pengguna. Mengacu pada rancangan evaluasi sistem pada Bab III, pengujian dilakukan melalui dua mekanisme utama, yaitu pengujian fungsional menggunakan Black Box Testing dan pengujian penerimaan pengguna menggunakan User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS).

### 4.7.1 Hasil Pengujian Fungsional (Black Box Testing)

Pengujian fungsional dilakukan untuk memverifikasi bahwa setiap fitur utama sistem menghasilkan keluaran yang sesuai dengan rancangan. Pengujian ini berfokus pada hubungan input-output tanpa menelaah struktur source code secara langsung. Ringkasan hasil pengujian fungsional ditunjukkan pada Tabel 4.13.

**Caption Tabel 4.13. Hasil pengujian fungsional sistem menggunakan Black Box Testing**

| No | Modul | Skenario Pengujian | Hasil yang Diharapkan | Hasil Aktual | Status |
|---|---|---|---|---|---|
| 1 | Login | Pengguna memasukkan username dan password yang valid | Sistem menampilkan dashboard utama | Dashboard utama berhasil ditampilkan setelah login | Berhasil |
| 2 | Login | Pengguna memasukkan username atau password yang tidak valid | Sistem menampilkan pesan kesalahan login | Pesan kesalahan login berhasil ditampilkan | Berhasil |
| 3 | Upload dan Analisis Data | Pengguna mengunggah file transaksi `.xlsx` yang valid dan menjalankan analisis | Sistem membaca file, memproses data, dan menampilkan hasil clustering | Hasil analisis berhasil ditampilkan, termasuk silhouette score dan profil cluster | Berhasil |
| 4 | Analisis Data | Pengguna menjalankan analisis tanpa mengunggah file | Sistem menolak proses analisis dan menampilkan peringatan | Peringatan untuk mengunggah file transaksi berhasil ditampilkan | Berhasil |
| 5 | Dashboard | Pengguna membuka halaman dashboard setelah login | Sistem menampilkan halaman utama analisis | Dashboard berhasil menampilkan halaman utama analisis | Berhasil |
| 6 | Riwayat Analisis | Pengguna membuka halaman riwayat analisis | Sistem menampilkan daftar hasil analisis yang pernah disimpan | Riwayat analisis berhasil ditampilkan | Berhasil |
| 7 | Detail Analisis | Pengguna membuka detail salah satu hasil analisis | Sistem menampilkan detail cluster, profil, dan ringkasan hasil analisis | Detail hasil analisis berhasil ditampilkan | Berhasil |
| 8 | Visualisasi Dendrogram | Pengguna membuka file visualisasi dendrogram hasil analisis | Sistem menampilkan gambar dendrogram sesuai hasil proses clustering | Gambar dendrogram berhasil ditampilkan | Berhasil |
| 9 | Laporan PDF | Pengguna mengunduh laporan hasil analisis | Sistem menghasilkan dan menampilkan file laporan PDF | File laporan PDF berhasil diunduh | Berhasil |

Berdasarkan Tabel 4.13 dapat diketahui bahwa seluruh fungsi utama sistem telah berjalan sesuai dengan hasil yang diharapkan. Dengan demikian, dari sisi fungsional, sistem telah memenuhi kebutuhan dasar penelitian.

### 4.7.2 Hasil Pengujian Penerimaan Pengguna (User Acceptance Testing)

Setelah sistem dinyatakan berjalan dengan baik secara fungsional, tahap berikutnya adalah pengujian penerimaan pengguna atau User Acceptance Testing (UAT). Sesuai rancangan Bab III, pengujian ini menggunakan instrumen System Usability Scale (SUS) yang terdiri dari 10 pernyataan dengan skala 1 sampai 5. Hasil akhirnya berupa skor 0 sampai 100, di mana sistem dinyatakan layak apabila memperoleh skor rata-rata minimal 68.

Bagian ini harus diisi berdasarkan hasil pengisian kuesioner oleh pengguna nyata atau expert users. Oleh karena itu, tabel berikut disiapkan sebagai format rekap hasil UAT yang nantinya dapat langsung diisi setelah pengujian dilakukan.

**Caption Tabel 4.14. Hasil rekapitulasi skor User Acceptance Testing menggunakan System Usability Scale**

| No | Responden | Peran/Jabatan | Total Skor Kontribusi | Skor SUS | Kategori |
|---|---|---|---:|---:|---|
| 1 | [Isi nama/inisial responden 1] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 2 | [Isi nama/inisial responden 2] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 3 | [Isi nama/inisial responden 3] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 4 | [Isi nama/inisial responden 4] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 5 | [Isi nama/inisial responden 5] | [Isi peran] | [Isi] | [Isi] | [Isi] |
|   | **Rata-rata** |  |  | **[Isi skor rata-rata SUS]** | **[Isi kategori akhir]** |

Narasi yang dapat digunakan setelah tabel di atas adalah sebagai berikut:

"Berdasarkan Tabel 4.14 dapat diketahui bahwa hasil User Acceptance Testing menggunakan metode System Usability Scale memperoleh skor rata-rata sebesar [isi skor rata-rata]. Nilai tersebut berada pada kategori [isi kategori] dan menunjukkan bahwa sistem [dapat/belum dapat] diterima oleh pengguna. Dengan demikian, dari sisi usability, sistem analisis segmentasi seasonality kunjungan Wisata Padusan [sudah memenuhi/belum memenuhi] kriteria kelayakan implementasi yang telah ditetapkan, yaitu skor SUS minimal 68."

## 4.8 Pembahasan

Berdasarkan hasil penelitian dapat diketahui bahwa sistem berhasil mengimplementasikan alur analisis yang telah dirancang pada Bab III, mulai dari pembacaan data transaksi mentah, pembersihan data, pembentukan matriks harian, normalisasi, proses Agglomerative Hierarchical Clustering, evaluasi jumlah cluster, hingga pembentukan rekomendasi bundling. Keberhasilan alur ini terlihat dari kemampuan sistem menghasilkan tiga cluster optimal dengan nilai Silhouette Score sebesar 0,6335. Nilai tersebut berada di atas ambang 0,5 yang pada Bab II telah dijelaskan sebagai indikator bahwa struktur cluster cukup baik untuk diinterpretasikan. Dengan demikian, hasil penelitian ini konsisten dengan konsep validasi Silhouette Coefficient yang diperkenalkan oleh Rousseeuw (1987).

Dari sisi metode, hasil penelitian juga memperkuat pemilihan Agglomerative Hierarchical Clustering (AHC) sebagai algoritma utama. AHC pada penelitian ini mampu membentuk struktur hierarkis dan menampilkan relasi antar-hari operasional melalui dendrogram. Temuan ini sejalan dengan kajian Guerard et al. (2025), Abdalla (2022), dan Van Ruitenbeek et al. (2023) yang menekankan bahwa pendekatan hierarkis sesuai untuk data yang memiliki pola fluktuatif dan tidak selalu stabil seperti data permintaan atau data kunjungan. Pada konteks penelitian ini, karakter temporal tersebut muncul pada variasi kunjungan harian, baik antara hari kerja, akhir pekan, maupun periode lonjakan tertentu.

Namun demikian, hasil pengelompokan pada data asli tidak membentuk tiga segmen musiman ideal yang sepenuhnya berbeda, misalnya `High Season`, `Weekend Pattern`, dan `Weekday Pattern` secara seimbang. Hasil aktual justru memperlihatkan dua cluster yang sama-sama berkarakter permintaan rendah dan satu cluster yang kuat pada dimensi akomodasi. Temuan ini penting karena menunjukkan bahwa seasonality pada data riil Wisata Padusan tidak selalu tampil dalam bentuk tiga musim yang tegas. Dengan kata lain, istilah seasonality dalam penelitian ini lebih tepat dimaknai sebagai pola kunjungan historis yang berulang, bukan pembagian musim yang harus selalu menghasilkan label yang seragam.

Jika dikaitkan dengan mekanisme rule generation pada Bab III, hasil penelitian ini tetap menunjukkan konsistensi antara rancangan metodologis dan luaran sistem. Cluster 2 diberi label `Staycation / Weekend Pattern` karena memiliki nilai centroid `Akomodasi` sebesar 0,5722, yaitu melampaui ambang dominansi yang dirumuskan dalam logika sistem. Sementara itu, Cluster 1 dan Cluster 3 diberi label `Low Season / Weekday` karena rerata permintaan pada kategori utamanya relatif rendah. Artinya, meskipun bentuk segmen akhir tidak sepenuhnya sama dengan ilustrasi awal pada proposal, sistem tetap bekerja sesuai aturan interpretasi yang telah dirancang.

Temuan ini sekaligus menegaskan pentingnya pendekatan data-driven. Penelitian ini tidak memaksa data untuk menyesuaikan asumsi peneliti, melainkan membiarkan data historis membentuk polanya sendiri. Pendekatan tersebut relevan dengan research gap yang telah dipaparkan pada Bab II, yaitu masih terbatasnya penelitian yang mengintegrasikan segmentasi seasonality berbasis AHC dengan perumusan strategi product bundling pada destinasi wisata alam. Oleh sebab itu, kontribusi utama penelitian ini tidak hanya terletak pada hasil clustering, tetapi juga pada keberhasilan membangun sistem yang menerjemahkan hasil clustering tersebut menjadi rekomendasi bisnis yang operasional.

Dari perspektif strategi pemasaran, rekomendasi bundling yang dihasilkan sistem juga masih sejalan dengan teori product bundling. Dominasi `Paket Hemat Weekday` dapat dipahami sebagai strategi untuk mendorong transaksi pada hari-hari dengan demand rendah. Hal ini selaras dengan Liu et al. (2025) yang menegaskan bahwa bundling dapat memengaruhi niat perilaku positif wisatawan, Nicolau dan Sellers (2020) yang menunjukkan bahwa bundling dapat menurunkan sensitivitas harga, serta Xu et al. (2016) yang menjelaskan bahwa bundling mampu meningkatkan nilai yang dirasakan pelanggan. Adapun `Paket Camping Adventure` pada Cluster 2 menunjukkan bahwa hasil segmentasi dapat diterjemahkan menjadi strategi diferensiasi layanan berbasis akomodasi.

Jika dikaitkan dengan bentuk bundling yang dibahas pada Bab II, rekomendasi pada penelitian ini cenderung mengarah pada pendekatan mixed bundling. Sistem tidak menghapus kemungkinan pembelian layanan secara terpisah, tetapi menawarkan kombinasi layanan tertentu sesuai profil cluster yang terbentuk. Pendekatan ini sejalan dengan penjelasan Huang dan Ho (2022) mengenai fleksibilitas bundling sebagai instrumen untuk meningkatkan perceived value konsumen.

Dengan demikian, pembahasan hasil penelitian ini menunjukkan bahwa sistem berhasil secara metodologis dan implementatif. Meskipun hasil segmentasi tidak sepenuhnya membentuk tiga label musim yang ideal, sistem tetap valid secara statistik, konsisten dengan rancangan metode, dan mampu menghasilkan rekomendasi yang relevan dengan karakter data historis Wisata Padusan.

## 4.9 Keterbatasan Hasil

Walaupun sistem berhasil membentuk cluster yang valid secara statistik, penelitian ini masih memiliki beberapa keterbatasan. Pertama, coverage kategori layanan tidak merata antar-tahun, terutama pada kategori `Akomodasi` yang muncul dalam proporsi sangat rendah pada sebagian besar tahun. Kedua, ditemukan lonjakan transaksi ekstrem yang tetap dipertahankan sebagai bagian dari pola historis, sehingga dapat memengaruhi struktur cluster. Ketiga, penelitian ini hanya menggunakan quantity transaksi dan belum memasukkan dimensi pendapatan secara langsung.

Ringkasan keterbatasan hasil analisis ditunjukkan pada Tabel 4.15.

**Caption Tabel 4.15. Ringkasan keterbatasan hasil analisis**

| Temuan | Keterangan |
|---|---|
| Coverage kategori tidak merata | Kategori akomodasi sangat rendah pada 2023-2025 sehingga pola staycation menjadi terbatas |
| Lonjakan transaksi ekstrem | Terdapat tanggal dengan nilai sangat tinggi, misalnya 29 Januari 2023 pada kategori Tiket Masuk dan Wahana Air |
| Variabel analisis terbatas pada quantity | Pendekatan belum memasukkan revenue, margin, atau kontribusi pendapatan per layanan |
| Hasil UAT belum diisikan | Pengujian penerimaan pengguna masih menunggu data responden nyata |

Secara keseluruhan, keterbatasan tersebut tidak membatalkan hasil penelitian, tetapi perlu dicatat sebagai konteks interpretasi. Dengan memahami keterbatasan ini, pembaca dapat menilai hasil clustering dan rekomendasi bundling secara lebih proporsional serta menjadikannya dasar bagi pengembangan penelitian selanjutnya.

## Daftar Caption Resmi Yang Bisa Langsung Dipakai

### Caption Tabel

- Tabel 4.1. Ringkasan dataset penelitian
- Tabel 4.2. Atribut utama data transaksi yang dimanfaatkan sistem
- Tabel 4.3. Rekap total quantity per tahun berdasarkan kategori utama
- Tabel 4.4. Hasil pembersihan data transaksi
- Tabel 4.5. Atribut hasil seleksi fitur pada tahap pra-pemrosesan
- Tabel 4.6. Skema generalisasi dan pemetaan kategori produk
- Tabel 4.7. Contoh lima baris pertama matriks harian hasil agregasi
- Tabel 4.8. Ringkasan hasil monitoring outlier berbasis IQR
- Tabel 4.9. Hasil evaluasi jumlah cluster menggunakan Silhouette Score
- Tabel 4.10. Ringkasan hasil cluster pada data asli
- Tabel 4.11. Nilai centroid cluster hasil analisis
- Tabel 4.12. Rekomendasi strategi product bundling berdasarkan hasil clustering
- Tabel 4.13. Hasil pengujian fungsional sistem menggunakan Black Box Testing
- Tabel 4.14. Hasil rekapitulasi skor User Acceptance Testing menggunakan System Usability Scale
- Tabel 4.15. Ringkasan keterbatasan hasil analisis

### Caption Gambar

- Gambar 4.1. Potongan kode pembacaan data transaksi
- Gambar 4.2. Potongan kode pembersihan data transaksi
- Gambar 4.3. Potongan kode generalisasi kategori produk
- Gambar 4.4. Potongan kode pembentukan matriks harian
- Gambar 4.5. Potongan kode monitoring outlier berbasis IQR
- Gambar 4.6. Dendrogram hasil Agglomerative Hierarchical Clustering pada data asli periode 2022-2025
- Gambar 4.7. Potongan kode evaluasi kandidat jumlah cluster
- Gambar 4.8. Potongan kode pembentukan cluster dan profiling
- Gambar 4.9. Potongan kode rule generation strategi bundling
- Gambar 4.10. Tampilan dashboard utama sistem analisis
- Gambar 4.11. Tampilan halaman riwayat dan detail hasil analisis
- Gambar 4.12. Tampilan laporan PDF hasil analisis
