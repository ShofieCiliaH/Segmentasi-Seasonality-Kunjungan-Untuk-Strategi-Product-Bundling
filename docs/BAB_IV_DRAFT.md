# BAB IV

# HASIL DAN PEMBAHASAN

Bab ini memaparkan hasil pengolahan data transaksi Wisata Padusan periode 1 Januari 2022 sampai dengan 30 November 2025 menggunakan metode Agglomerative Hierarchical Clustering (AHC) serta pembahasan terhadap pola segmentasi yang dihasilkan. Uraian pada bab ini mencakup gambaran data penelitian, hasil pra-pemrosesan, evaluasi jumlah cluster, profil cluster, rekomendasi strategi product bundling, implementasi sistem, hasil pengujian sistem, pembahasan, hingga keterbatasan hasil analisis.

## 4.1 Gambaran Data Penelitian

Data yang digunakan dalam penelitian ini merupakan data transaksi Wisata Padusan periode 1 Januari 2022 sampai dengan 30 November 2025. Data diperoleh dalam bentuk file tahunan, yaitu 2022.xlsx, 2023.xlsx, 2024.xlsx, dan 2025.xlsx, yang kemudian digabungkan menjadi satu dataset untuk proses analisis. Penggabungan data dilakukan agar sistem dapat membaca pola kunjungan secara berkelanjutan lintas tahun sehingga karakteristik seasonality dapat diamati secara lebih utuh.

Berdasarkan hasil penggabungan data, diperoleh 13.586 baris transaksi dengan 1.427 hari operasional unik. Rentang waktu yang tercakup dalam data dimulai pada 1 Januari 2022 dan berakhir pada 30 November 2025. Ringkasan dataset penelitian disajikan pada Tabel 4.1.

**Caption Tabel 4.1. Ringkasan dataset penelitian**

| Komponen | Nilai |
|---|---|
| Periode data | 1 Januari 2022 - 30 November 2025 |
| Jumlah file sumber | 4 file tahunan |
| Nama file sumber | 2022.xlsx, 2023.xlsx, 2024.xlsx, 2025.xlsx |
| Jumlah baris awal | 13.586 |
| Jumlah hari operasional unik | 1.427 |

Selain ringkasan umum dataset, distribusi volume transaksi per tahun juga penting untuk memberikan gambaran skala operasional. Rekapitulasi total quantity berdasarkan kategori utama hasil generalisasi ditampilkan pada Tabel 4.2.

**Caption Tabel 4.2. Rekap total quantity per tahun berdasarkan kategori utama**

| Tahun | Akomodasi | De Qoem (VIP) | Parkir | Tiket Masuk | Wahana Air |
|---|---:|---:|---:|---:|---:|
| 2022 | 277 | 2.038 | 44.550 | 148.220 | 111.076 |
| 2023 | 16 | 3.149 | 123.814 | 375.236 | 313.313 |
| 2024 | 6 | 3.546 | 147.082 | 384.214 | 403.746 |
| 2025 | 5 | 2.950 | 129.975 | 316.828 | 352.928 |

Berdasarkan Tabel 4.2 dapat diketahui bahwa kategori dengan volume tertinggi secara umum berada pada layanan Tiket Masuk dan Wahana Air. Tahun 2024 menjadi periode dengan total quantity tertinggi pada kategori Tiket Masuk dan Wahana Air. Hal ini menunjukkan bahwa pola permintaan utama pengunjung lebih banyak terkonsentrasi pada kunjungan reguler dan penggunaan fasilitas wahana air.

## 4.2 Hasil Pra-pemrosesan Data

Pada tahap ini dilakukan pra-pemrosesan data untuk memastikan bahwa data yang masuk ke algoritma clustering berada dalam kondisi yang bersih, konsisten, dan representatif terhadap perilaku pembelian pengunjung. Proses ini meliputi validasi tanggal, validasi nilai jumlah, penghapusan data non-tiket, serta pemetaan nama layanan ke dalam kategori produk utama.

Hasil pembersihan data menunjukkan bahwa tidak seluruh baris transaksi dapat langsung digunakan. Sebagian data dieliminasi karena mengandung tanggal tidak valid, nilai jumlah kosong, jumlah bernilai nol, atau mengandung kata kunci yang mengindikasikan bahwa transaksi tersebut bukan merupakan pembelian tiket pengunjung. Ringkasan hasil pra-pemrosesan disajikan pada Tabel 4.3.

**Caption Tabel 4.3. Hasil pra-pemrosesan data transaksi**

| Jenis pembersihan | Jumlah baris |
|---|---:|
| Tanggal tidak valid | 43 |
| Nilai jumlah kosong | 66 |
| Jumlah bernilai 0 | 100 |
| Data non-tiket/keyword tidak relevan | 56 |
| Data tidak terkategori | 65 |
| Total baris tereliminasi | 330 |
| Total baris valid | 13.256 |

Berdasarkan Tabel 4.3 dapat diketahui bahwa dari total 13.586 baris transaksi awal, sebanyak 330 baris data dieliminasi dan tersisa 13.256 baris data valid yang digunakan dalam analisis. Dengan demikian, mayoritas data masih dapat dipertahankan sehingga informasi historis yang tersedia tetap cukup kuat untuk mendukung proses clustering.

Selanjutnya, dilakukan evaluasi terhadap kelengkapan kategori layanan per tahun. Langkah ini penting karena ketidakseimbangan kemunculan kategori tertentu dapat memengaruhi pembentukan pola cluster. Persentase hari yang memuat transaksi pada masing-masing kategori utama ditunjukkan pada Tabel 4.4.

**Caption Tabel 4.4. Persentase kemunculan kategori utama per hari menurut tahun**

| Tahun | Akomodasi | De Qoem (VIP) | Parkir | Tiket Masuk | Wahana Air |
|---|---:|---:|---:|---:|---:|
| 2022 | 19,2% | 95,3% | 46,8% | 47,1% | 100,0% |
| 2023 | 3,6% | 96,2% | 83,3% | 84,1% | 100,0% |
| 2024 | 1,7% | 98,3% | 100,0% | 100,0% | 99,2% |
| 2025 | 1,5% | 99,7% | 100,0% | 100,0% | 100,0% |

Berdasarkan Tabel 4.4 dapat diketahui bahwa coverage kategori Akomodasi relatif rendah, terutama pada tahun 2023 sampai 2025. Sebaliknya, kategori De Qoem (VIP) dan Wahana Air muncul hampir pada seluruh tahun secara konsisten. Hal ini menunjukkan bahwa struktur data historis antar kategori tidak sepenuhnya seimbang, sehingga hasil cluster yang terbentuk sangat mungkin dipengaruhi oleh dominasi kategori tertentu.

## 4.3 Hasil Penentuan Jumlah Cluster

Setelah tahap pra-pemrosesan selesai, data ditransformasikan ke dalam bentuk matriks harian berdasarkan kategori produk hasil generalisasi. Setiap baris mewakili satu hari operasional, sedangkan setiap kolom mewakili kategori layanan utama, yaitu Akomodasi, De Qoem (VIP), Parkir, Tiket Masuk, dan Wahana Air. Data matriks tersebut kemudian dinormalisasi menggunakan Min-Max Scaler sebelum diproses menggunakan algoritma Agglomerative Hierarchical Clustering dengan Ward linkage.

Penentuan jumlah cluster dilakukan dengan membandingkan nilai Silhouette Score pada beberapa kandidat nilai k, yaitu dari k = 2 sampai dengan k = 6. Hasil evaluasi ditunjukkan pada Tabel 4.5.

**Caption Tabel 4.5. Hasil evaluasi jumlah cluster menggunakan Silhouette Score**

| Nilai k | Silhouette Score |
|---:|---:|
| 2 | 0,6128 |
| 3 | 0,6335 |
| 4 | 0,4640 |
| 5 | 0,4681 |
| 6 | 0,4704 |

Berdasarkan Tabel 4.5 dapat diketahui bahwa nilai Silhouette Score tertinggi diperoleh pada k = 3, yaitu sebesar 0,6335. Oleh karena itu, jumlah cluster yang digunakan dalam analisis utama penelitian ini adalah tiga cluster. Nilai tersebut berada di atas ambang validitas 0,5 sehingga struktur cluster yang terbentuk dapat dikategorikan cukup baik untuk diinterpretasikan lebih lanjut.

Selain melalui evaluasi numerik, struktur hierarki pengelompokan juga divisualisasikan dalam bentuk dendrogram. Visualisasi ini ditampilkan pada Gambar 4.1.

**Caption Gambar 4.1. Dendrogram hasil Agglomerative Hierarchical Clustering pada data asli periode 2022-2025**

Gunakan gambar:

`D:\laragon\www\skripsi2\storage\generated\plots\dendrogram-data-asli-2022-2025.png`

Narasi setelah gambar:

Gambar 4.1 menunjukkan hubungan hierarkis antar hari operasional berdasarkan kemiripan pola penjualan. Pemotongan dendrogram pada jumlah cluster optimal menghasilkan tiga kelompok utama yang kemudian dianalisis lebih lanjut melalui nilai centroid dan karakteristik seasonality masing-masing cluster.

## 4.4 Hasil Clustering dan Profil Cluster

Hasil pengelompokan menggunakan k = 3 menghasilkan tiga kelompok hari operasional dengan jumlah anggota dan karakteristik yang berbeda. Sistem selanjutnya menghitung nilai centroid dari masing-masing cluster untuk setiap kategori produk guna memperoleh profil segmentasi. Ringkasan hasil cluster disajikan pada Tabel 4.6.

**Caption Tabel 4.6. Ringkasan hasil cluster pada data asli**

| Cluster | Jumlah Hari | Proporsi Akhir Pekan | Label Sistem | Paket Rekomendasi |
|---|---:|---:|---|---|
| Cluster 1 | 336 | 75,6% | Low Season / Weekday | Paket Hemat Weekday |
| Cluster 2 | 30 | 73,3% | Staycation / Weekend Pattern | Paket Camping Adventure |
| Cluster 3 | 1.061 | 12,6% | Low Season / Weekday | Paket Hemat Weekday |

Untuk memperoleh pemahaman yang lebih rinci, nilai centroid masing-masing cluster terhadap setiap kategori utama ditampilkan pada Tabel 4.7.

**Caption Tabel 4.7. Nilai centroid cluster hasil analisis**

| Cluster | Tiket Masuk | Parkir | Wahana Air | Akomodasi | De Qoem (VIP) |
|---|---:|---:|---:|---:|---:|
| Cluster 1 | 0,0953 | 0,0801 | 0,0871 | 0,0074 | 0,2833 |
| Cluster 2 | 0,1023 | 0,0714 | 0,0610 | 0,5722 | 0,1764 |
| Cluster 3 | 0,0151 | 0,0143 | 0,0196 | 0,0053 | 0,0747 |

Berdasarkan Tabel 4.7 dapat diketahui bahwa Cluster 2 memiliki nilai tertinggi pada kategori Akomodasi, yaitu sebesar 0,5722. Nilai ini jauh lebih tinggi dibandingkan dua cluster lainnya sehingga cluster tersebut diidentifikasi oleh sistem sebagai Staycation / Weekend Pattern. Sementara itu, Cluster 1 dan Cluster 3 menunjukkan nilai yang relatif rendah pada hampir seluruh kategori utama, sehingga sistem mengklasifikasikannya ke dalam pola Low Season / Weekday.

Secara rinci, interpretasi setiap cluster adalah sebagai berikut.

### 4.4.1 Cluster 1

Cluster 1 terdiri dari 336 hari operasional. Proporsi hari akhir pekan pada cluster ini sebesar 75,6%, sehingga secara komposisi waktu cluster ini cukup banyak berisi hari Sabtu dan Minggu. Namun demikian, nilai centroid seluruh kategori utama selain De Qoem (VIP) tetap berada pada level rendah. Oleh karena itu, sistem memberikan label Low Season / Weekday dan mengusulkan strategi Paket Hemat Weekday.

Temuan ini menunjukkan bahwa keberadaan hari akhir pekan tidak selalu identik dengan lonjakan kuantitas tinggi pada seluruh kategori layanan. Pada data asli, terdapat cukup banyak hari akhir pekan yang tidak menampilkan pola permintaan sangat tinggi, sehingga oleh sistem tetap dikelompokkan bersama hari dengan intensitas permintaan yang rendah hingga sedang.

### 4.4.2 Cluster 2

Cluster 2 terdiri dari 30 hari operasional dengan proporsi akhir pekan sebesar 73,3%. Nilai centroid tertinggi cluster ini terletak pada kategori Akomodasi, yaitu 0,5722. Berdasarkan rule yang diterapkan, cluster ini diidentifikasi sebagai Staycation / Weekend Pattern dan direkomendasikan untuk strategi Paket Camping Adventure.

Hasil ini menunjukkan bahwa pada sebagian hari tertentu, terutama yang banyak jatuh pada akhir pekan, pola kunjungan cenderung lebih menonjol pada penggunaan layanan menginap atau akomodasi dibandingkan kombinasi kunjungan massal ke seluruh wahana.

### 4.4.3 Cluster 3

Cluster 3 merupakan cluster dengan anggota terbanyak, yaitu 1.061 hari operasional. Proporsi hari akhir pekan hanya sebesar 12,6%, sehingga cluster ini lebih banyak terdiri dari hari kerja biasa. Nilai centroid pada seluruh kategori utama merupakan yang paling rendah dibandingkan cluster lain, yaitu Tiket Masuk 0,0151, Parkir 0,0143, Wahana Air 0,0196, Akomodasi 0,0053, dan De Qoem (VIP) 0,0747.

Berdasarkan hasil tersebut, sistem memberikan label Low Season / Weekday dan mengusulkan Paket Hemat Weekday. Cluster ini merepresentasikan kondisi operasional dengan intensitas permintaan paling rendah dan paling dominan dalam keseluruhan dataset.

## 4.5 Hasil Rekomendasi Strategi Product Bundling

Berdasarkan hasil profiling cluster, sistem menghasilkan dua rekomendasi strategi bundling utama, yaitu Paket Hemat Weekday dan Paket Camping Adventure. Hasil rekomendasi tersebut dirangkum pada Tabel 4.8.

**Caption Tabel 4.8. Rekomendasi strategi product bundling berdasarkan hasil clustering**

| Cluster | Label Sistem | Strategi Bundling | Komposisi |
|---|---|---|---|
| Cluster 1 | Low Season / Weekday | Paket Hemat Weekday | Tiket Masuk + Parkir |
| Cluster 2 | Staycation / Weekend Pattern | Paket Camping Adventure | Tiket Masuk + Akomodasi |
| Cluster 3 | Low Season / Weekday | Paket Hemat Weekday | Tiket Masuk + Parkir |

Berdasarkan Tabel 4.8 dapat diketahui bahwa rekomendasi Paket Hemat Weekday muncul sebagai strategi dominan karena dua dari tiga cluster memiliki karakteristik permintaan relatif rendah. Sementara itu, Paket Camping Adventure hanya muncul pada cluster yang memperlihatkan dominasi kategori akomodasi. Dengan demikian, hasil sistem menunjukkan bahwa pola bundling pada data asli belum sepenuhnya didominasi oleh paket high season, melainkan lebih banyak diarahkan pada strategi efisiensi transaksi pada hari dengan permintaan rendah serta strategi staycation pada hari tertentu.

## 4.6 Hasil Implementasi Sistem

Sebagai bagian dari penelitian, model analitik yang dibangun tidak hanya berhenti pada pengujian komputasional, tetapi juga diimplementasikan ke dalam bentuk aplikasi dashboard. Sistem ini memungkinkan pengguna mengunggah file transaksi, menjalankan analisis clustering, melihat visualisasi dendrogram, membaca profil cluster, mengakses riwayat analisis, dan mengunduh laporan dalam format PDF.

**Caption Gambar 4.2. Tampilan dashboard utama sistem analisis bundling**

Saran gambar:

Gunakan screenshot halaman dashboard setelah data asli dimuat.

**Caption Gambar 4.3. Tampilan halaman riwayat analisis**

Saran gambar:

Gunakan screenshot halaman riwayat untuk menunjukkan bahwa hasil analisis dapat disimpan dan dipanggil kembali.

**Caption Gambar 4.4. Tampilan laporan PDF hasil analisis**

Saran gambar:

Gunakan screenshot file PDF hasil analisis dari aplikasi.

Narasi:

Implementasi sistem ini memperlihatkan bahwa seluruh tahapan yang dirancang pada proposal, mulai dari input data, pemrosesan clustering, hingga penyajian hasil rekomendasi, telah dapat diwujudkan dalam bentuk aplikasi yang dapat digunakan secara langsung oleh pengguna internal. Dengan demikian, penelitian ini tidak hanya menghasilkan model analitik, tetapi juga perangkat lunak fungsional yang mendukung pengambilan keputusan berbasis data.

## 4.7 Hasil Pengujian Sistem

Pengujian sistem pada penelitian ini dilakukan untuk mengetahui apakah sistem yang dibangun telah berfungsi sesuai kebutuhan dan dapat diterima oleh pengguna. Mengacu pada rancangan evaluasi sistem pada Bab III, pengujian dilakukan melalui dua mekanisme utama, yaitu pengujian fungsional menggunakan Black Box Testing dan pengujian penerimaan pengguna menggunakan User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS).

### 4.7.1 Hasil Pengujian Fungsional (Black Box Testing)

Pengujian fungsional dilakukan untuk memverifikasi bahwa setiap fitur utama sistem dapat berjalan sesuai dengan keluaran yang diharapkan. Pengujian ini berfokus pada input dan output sistem tanpa meninjau struktur kode program secara langsung. Modul yang diuji meliputi proses login, unggah data transaksi, analisis clustering, tampilan hasil, riwayat analisis, visualisasi dendrogram, dan unduh laporan PDF.

**Caption Tabel 4.9. Hasil pengujian fungsional sistem menggunakan Black Box Testing**

| No | Modul | Skenario Pengujian | Hasil yang Diharapkan | Hasil Aktual | Status |
|---|---|---|---|---|---|
| 1 | Login | Pengguna memasukkan username dan password yang valid | Sistem menampilkan dashboard utama | Dashboard utama berhasil ditampilkan setelah login | Berhasil |
| 2 | Login | Pengguna memasukkan username atau password yang tidak valid | Sistem menampilkan pesan kesalahan login | Pesan kesalahan login berhasil ditampilkan | Berhasil |
| 3 | Upload dan Analisis Data | Pengguna mengunggah file transaksi `.xlsx` yang valid dan menjalankan analisis | Sistem membaca file, memproses data, dan menampilkan hasil clustering | Hasil analisis berhasil ditampilkan, termasuk silhouette score dan profil cluster | Berhasil |
| 4 | Analisis Data | Pengguna menjalankan analisis tanpa mengunggah file | Sistem menolak proses analisis dan menampilkan peringatan | Peringatan untuk mengunggah file transaksi berhasil ditampilkan | Berhasil |
| 5 | Dashboard | Pengguna membuka halaman dashboard setelah login | Sistem menampilkan ringkasan hasil analisis terbaru | Dashboard berhasil menampilkan ringkasan hasil analisis | Berhasil |
| 6 | Riwayat Analisis | Pengguna membuka halaman riwayat analisis | Sistem menampilkan daftar hasil analisis yang pernah disimpan | Riwayat analisis berhasil ditampilkan | Berhasil |
| 7 | Detail Analisis | Pengguna membuka detail salah satu hasil analisis | Sistem menampilkan detail cluster, profil, dan ringkasan hasil analisis | Detail hasil analisis berhasil ditampilkan | Berhasil |
| 8 | Visualisasi Dendrogram | Pengguna membuka file visualisasi dendrogram hasil analisis | Sistem menampilkan gambar dendrogram sesuai hasil proses clustering | Gambar dendrogram berhasil ditampilkan | Berhasil |
| 9 | Laporan PDF | Pengguna mengunduh laporan hasil analisis | Sistem menghasilkan dan menampilkan file laporan PDF | File laporan PDF berhasil diunduh | Berhasil |

Berdasarkan Tabel 4.9 dapat diketahui bahwa seluruh fungsi utama pada sistem telah berjalan sesuai dengan hasil yang diharapkan. Proses autentikasi pengguna, unggah data transaksi, analisis clustering, penyimpanan riwayat, tampilan detail analisis, visualisasi dendrogram, serta pembuatan laporan PDF dapat dijalankan dengan baik. Dengan demikian, sistem yang dibangun telah memenuhi kebutuhan fungsional utama penelitian.

### 4.7.2 Hasil Pengujian Penerimaan Pengguna (User Acceptance Testing)

Setelah sistem dinyatakan valid secara fungsional, tahap berikutnya adalah pengujian penerimaan pengguna atau User Acceptance Testing (UAT). Pengujian ini bertujuan untuk mengetahui tingkat penerimaan, kemudahan penggunaan, dan kenyamanan pengguna terhadap antarmuka serta luaran sistem. Sesuai rancangan pada Bab III, pengukuran UAT dilakukan menggunakan instrumen System Usability Scale (SUS).

Instrumen SUS terdiri dari 10 pernyataan dengan skala Likert 1 sampai 5. Nilai jawaban dari setiap responden kemudian dikonversi menjadi skor SUS dengan rentang 0 sampai 100. Semakin tinggi skor yang diperoleh, semakin baik tingkat usability sistem. Berdasarkan acuan pada Bab II, sistem dinyatakan layak apabila memperoleh skor SUS rata-rata minimal 68, yang termasuk kategori acceptable.

Bagian ini tidak boleh diisi secara asumtif. Hasil UAT harus berasal dari pengisian kuesioner oleh pengguna nyata atau expert users yang relevan dengan konteks sistem, misalnya pihak manajemen, staf digitalisasi, atau pengguna internal terkait di PT Palawi Risorsis/Wisata Padusan.

**Caption Tabel 4.10. Hasil rekapitulasi skor User Acceptance Testing menggunakan System Usability Scale**

| No | Responden | Peran/Jabatan | Total Skor Kontribusi | Skor SUS | Kategori |
|---|---|---|---:|---:|---|
| 1 | [Isi nama/inisial responden 1] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 2 | [Isi nama/inisial responden 2] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 3 | [Isi nama/inisial responden 3] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 4 | [Isi nama/inisial responden 4] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 5 | [Isi nama/inisial responden 5] | [Isi peran] | [Isi] | [Isi] | [Isi] |
|   | **Rata-rata** |  |  | **[Isi skor rata-rata SUS]** | **[Isi kategori akhir]** |

Narasi yang dapat digunakan setelah tabel di atas adalah sebagai berikut:

"Berdasarkan Tabel 4.10 dapat diketahui bahwa hasil User Acceptance Testing menggunakan metode System Usability Scale memperoleh skor rata-rata sebesar [isi skor rata-rata]. Nilai tersebut berada pada kategori [isi kategori] dan menunjukkan bahwa sistem [dapat/belum dapat] diterima oleh pengguna. Dengan demikian, dari sisi usability, sistem analisis segmentasi seasonality kunjungan Wisata Padusan [sudah memenuhi/belum memenuhi] kriteria kelayakan implementasi yang telah ditetapkan, yaitu skor SUS minimal 68."

## 4.8 Pembahasan

Berdasarkan hasil analisis terhadap data asli dapat diketahui bahwa sistem berhasil membentuk segmentasi hari operasional berdasarkan kemiripan pola penjualan layanan. Keberhasilan tersebut ditunjukkan oleh nilai Silhouette Score sebesar 0,6335 pada k = 3. Nilai ini berada di atas ambang 0,5 yang pada Bab II dijelaskan sebagai indikator bahwa struktur cluster telah terpisah dengan cukup baik. Dengan demikian, hasil penelitian ini sejalan dengan konsep validasi Silhouette Coefficient yang diperkenalkan oleh Rousseeuw (1987) dan digunakan secara luas dalam literatur data mining modern. Secara teoritis, nilai siluet yang positif dan mendekati 1 menunjukkan bahwa objek lebih dekat dengan cluster-nya sendiri dibandingkan dengan cluster lain, sehingga hasil pengelompokan dapat dinilai layak untuk diinterpretasikan lebih lanjut.

Dari sisi metode, hasil penelitian ini juga mendukung landasan teoritis pada Bab II yang menyatakan bahwa Agglomerative Hierarchical Clustering (AHC) sesuai untuk data yang memiliki struktur hierarkis, fluktuasi tinggi, dan karakter temporal seperti seasonality kunjungan wisata. Temuan ini sejalan dengan kajian Guerard et al. (2025) dan Abdalla (2022) yang menunjukkan bahwa AHC mampu menangkap struktur data lebih baik dibandingkan metode partisional pada konteks tertentu, serta konsisten dengan Van Ruitenbeek et al. (2023) yang menekankan keunggulan pendekatan hierarkis dalam menghadapi pola permintaan yang tidak stabil. Pada penelitian ini, AHC tidak hanya mampu membentuk cluster yang valid, tetapi juga menghasilkan dendrogram yang membantu proses interpretasi hubungan antar hari operasional secara hierarkis.

Namun demikian, hasil segmentasi yang diperoleh tidak sepenuhnya menunjukkan terbentuknya tiga segmen musiman ideal seperti High Season, Weekend Pattern, dan Weekday Pattern secara seimbang. Pada data asli, sistem justru menghasilkan dua cluster yang sama-sama berkarakter permintaan relatif rendah serta satu cluster yang lebih dekat dengan pola staycation atau akomodasi. Temuan ini menunjukkan bahwa pola seasonality aktual pada Wisata Padusan tidak selalu identik dengan asumsi awal bahwa kunjungan akan terbelah tegas ke dalam segmen ramai, sedang, dan rendah. Dengan kata lain, konsep seasonality dalam penelitian ini lebih tepat dipahami sebagai pola kunjungan historis yang berulang, bukan sebagai pembagian musim yang harus selalu menghasilkan tiga label yang sepenuhnya berbeda.

Jika dikaitkan dengan mekanisme rule generation yang telah dirancang pada Bab III, hasil ini juga menunjukkan konsistensi antara rancangan metodologis dan luaran sistem. Cluster 2 diberi label Staycation / Weekend Pattern karena memiliki nilai centroid Akomodasi sebesar 0,5722, yaitu melampaui ambang batas dominansi yang ditetapkan dalam rancangan rule. Sebaliknya, Cluster 1 dan Cluster 3 memperoleh label Low Season / Weekday karena nilai rata-rata kategori utamanya relatif rendah. Artinya, walaupun keluaran akhir tidak sepenuhnya sama dengan ilustrasi cluster ideal pada proposal, sistem tetap bekerja sesuai logika interpretasi yang dirancang sejak awal penelitian.

Interpretasi tersebut memperlihatkan pentingnya pendekatan data-driven dalam penelitian ini. Sistem tidak diposisikan untuk memaksakan pola tertentu, tetapi untuk membaca pola yang benar-benar muncul dalam data historis. Pada titik ini, hasil penelitian sekaligus menegaskan research gap yang telah dipaparkan pada Bab II, yaitu belum banyak penelitian yang secara langsung mengintegrasikan segmentasi berbasis seasonality menggunakan AHC dengan penyusunan strategi product bundling pada destinasi wisata alam. Oleh sebab itu, walaupun hasil cluster tidak seluruhnya sesuai dengan ekspektasi awal, penelitian ini tetap memberikan kontribusi penting berupa integrasi antara analisis clustering, interpretasi musim kunjungan, dan perumusan rekomendasi bisnis dalam satu sistem yang utuh.

Selain itu, hasil analisis juga menunjukkan bahwa rekomendasi bundling yang dihasilkan sistem cenderung lebih konservatif, yakni dominan pada Paket Hemat Weekday, serta satu rekomendasi Paket Camping Adventure untuk cluster dengan karakteristik akomodasi tinggi. Dari perspektif teori pemasaran, temuan ini masih relevan dengan landasan product bundling pada Bab II. Liu et al. (2025) menjelaskan bahwa bundling dapat memengaruhi niat perilaku positif wisatawan, Nicolau dan Sellers (2020) menekankan bahwa bundling dapat menurunkan sensitivitas harga melalui efek loss aversion, sedangkan Xu et al. (2016) menunjukkan bahwa bundling mampu meningkatkan nilai yang dirasakan wisatawan. Oleh karena itu, rekomendasi Paket Hemat Weekday pada periode permintaan rendah dapat dipahami sebagai strategi untuk meningkatkan daya tarik transaksi, sedangkan Paket Camping Adventure dapat dipandang sebagai strategi diferensiasi layanan pada cluster yang menunjukkan minat lebih tinggi terhadap akomodasi.

Apabila dikaitkan dengan bentuk bundling yang dibahas pada Bab II, rekomendasi sistem pada penelitian ini juga cenderung mengarah pada pendekatan mixed bundling, yaitu menawarkan kombinasi layanan yang relevan tanpa menghilangkan kemungkinan pembelian layanan secara terpisah. Hal ini sesuai dengan penjelasan Huang dan Ho (2022) mengenai fleksibilitas bundling sebagai instrumen untuk meningkatkan perceived value konsumen. Dengan demikian, hasil penelitian ini tidak hanya mendukung penggunaan AHC sebagai metode segmentasi, tetapi juga memperlihatkan bahwa keluaran segmentasi dapat diterjemahkan menjadi strategi bundling yang operasional dan kontekstual.

Temuan ini dapat menjadi bahan pertimbangan penting bagi manajemen. Apabila tujuan bisnis perusahaan adalah meningkatkan cross-selling pada hari-hari permintaan rendah, maka rekomendasi sistem sudah cukup relevan. Namun apabila perusahaan ingin fokus pada strategi bundling untuk momen high season, maka diperlukan evaluasi lanjutan terhadap kualitas data, struktur pencatatan transaksi, serta kemungkinan pengayaan variabel analisis. Dengan demikian, pembahasan hasil penelitian ini menunjukkan bahwa sistem telah berhasil secara metodologis dan fungsional, tetapi interpretasi strategisnya tetap harus dibaca dengan mempertimbangkan karakter data operasional yang menjadi dasar analisis.

## 4.9 Keterbatasan Hasil

Walaupun sistem berhasil menghasilkan cluster yang valid secara statistik, penelitian ini masih memiliki beberapa keterbatasan. Pertama, coverage kategori layanan tidak merata antar tahun. Kategori akomodasi, misalnya, muncul dalam persentase yang sangat rendah pada sebagian besar tahun, sehingga kekuatan pola staycation dalam data menjadi terbatas.

Kedua, ditemukan nilai transaksi yang sangat ekstrem pada tanggal tertentu. Salah satu contoh paling menonjol adalah tanggal 29 Januari 2023, yang menunjukkan penjualan Tiket Masuk sebesar 23.938 dan Wahana Air sebesar 22.770, sementara Parkir bernilai 0. Data ini dipertahankan apa adanya dalam analisis utama untuk menjaga integritas data asli, namun sangat mungkin memengaruhi pembentukan struktur cluster.

Ketiga, penelitian ini hanya menggunakan variabel quantity atau jumlah transaksi sebagai dasar clustering. Pendekatan ini sesuai dengan batasan penelitian, namun belum memasukkan aspek nilai ekonomi seperti pendapatan atau revenue contribution yang mungkin akan memperkaya interpretasi strategi bundling.

Ringkasan keterbatasan hasil ditunjukkan pada Tabel 4.11.

**Caption Tabel 4.11. Ringkasan keterbatasan hasil analisis**

| Temuan | Keterangan |
|---|---|
| Tanggal tidak valid | 43 baris |
| Nilai jumlah kosong | 66 baris |
| Jumlah bernilai 0 | 100 baris |
| Coverage kategori tidak merata | terutama pada kategori Akomodasi |
| Tanggal ekstrem | 29 Januari 2023 menunjukkan lonjakan sangat tinggi |
| Variabel analisis | terbatas pada quantity, belum memasukkan revenue |

Untuk memperjelas temuan tanggal ekstrem tersebut, detail ringkasnya dapat ditampilkan pada Tabel 4.12.

**Caption Tabel 4.12. Contoh tanggal ekstrem yang teridentifikasi pada data asli**

| Tanggal | Tiket Masuk | Wahana Air | Parkir | Catatan |
|---|---:|---:|---:|---|
| 29 Januari 2023 | 23.938 | 22.770 | 0 | Nilai sangat ekstrem dibandingkan hari lainnya |

Berdasarkan uraian di atas, hasil penelitian ini tetap menunjukkan bahwa sistem mampu menjalankan segmentasi seasonality berbasis data historis secara objektif. Meskipun demikian, interpretasi hasil perlu dilakukan dengan mempertimbangkan kondisi kualitas data operasional yang tersedia. Oleh karena itu, penelitian ini dapat dipandang sebagai landasan awal yang kuat untuk pengembangan sistem rekomendasi bundling berbasis data pada penelitian lanjutan.

---

## Daftar Caption Resmi Yang Bisa Langsung Dipakai

### Caption Tabel

- Tabel 4.1. Ringkasan dataset penelitian
- Tabel 4.2. Rekap total quantity per tahun berdasarkan kategori utama
- Tabel 4.3. Hasil pra-pemrosesan data transaksi
- Tabel 4.4. Persentase kemunculan kategori utama per hari menurut tahun
- Tabel 4.5. Hasil evaluasi jumlah cluster menggunakan Silhouette Score
- Tabel 4.6. Ringkasan hasil cluster pada data asli
- Tabel 4.7. Nilai centroid cluster hasil analisis
- Tabel 4.8. Rekomendasi strategi product bundling berdasarkan hasil clustering
- Tabel 4.9. Hasil pengujian fungsional sistem menggunakan Black Box Testing
- Tabel 4.10. Hasil rekapitulasi skor User Acceptance Testing menggunakan System Usability Scale
- Tabel 4.11. Ringkasan keterbatasan hasil analisis
- Tabel 4.12. Contoh tanggal ekstrem yang teridentifikasi pada data asli

### Caption Gambar

- Gambar 4.1. Dendrogram hasil Agglomerative Hierarchical Clustering pada data asli periode 2022-2025
- Gambar 4.2. Tampilan dashboard utama sistem analisis bundling
- Gambar 4.3. Tampilan halaman riwayat analisis
- Gambar 4.4. Tampilan laporan PDF hasil analisis
