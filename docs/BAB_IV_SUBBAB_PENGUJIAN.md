## 4.x Hasil Pengujian Sistem

Pengujian sistem pada penelitian ini dilakukan untuk mengetahui apakah sistem yang dibangun telah berfungsi sesuai kebutuhan dan dapat diterima oleh pengguna. Mengacu pada rancangan evaluasi sistem pada Bab III, pengujian dilakukan melalui dua mekanisme utama, yaitu pengujian fungsional menggunakan Black Box Testing dan pengujian penerimaan pengguna menggunakan User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS).

### 4.x.1 Hasil Pengujian Fungsional (Black Box Testing)

Pengujian fungsional dilakukan untuk memverifikasi bahwa setiap fitur utama sistem dapat berjalan sesuai dengan keluaran yang diharapkan. Pengujian ini berfokus pada input dan output sistem tanpa meninjau struktur kode program secara langsung. Modul yang diuji meliputi proses login, unggah data transaksi, analisis clustering, tampilan hasil, riwayat analisis, visualisasi dendrogram, dan unduh laporan PDF.

**Caption Tabel 4.xx. Hasil pengujian fungsional sistem menggunakan Black Box Testing**

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

Berdasarkan Tabel 4.xx dapat diketahui bahwa seluruh fungsi utama pada sistem telah berjalan sesuai dengan hasil yang diharapkan. Proses autentikasi pengguna, unggah data transaksi, analisis clustering, penyimpanan riwayat, tampilan detail analisis, visualisasi dendrogram, serta pembuatan laporan PDF dapat dijalankan dengan baik. Dengan demikian, sistem yang dibangun telah memenuhi kebutuhan fungsional utama penelitian.

### 4.x.2 Hasil Pengujian Penerimaan Pengguna (User Acceptance Testing)

Setelah sistem dinyatakan valid secara fungsional, tahap berikutnya adalah pengujian penerimaan pengguna atau User Acceptance Testing (UAT). Pengujian ini bertujuan untuk mengetahui tingkat penerimaan, kemudahan penggunaan, dan kenyamanan pengguna terhadap antarmuka serta luaran sistem. Sesuai rancangan pada Bab III, pengukuran UAT dilakukan menggunakan instrumen System Usability Scale (SUS).

Instrumen SUS terdiri dari 10 pernyataan dengan skala Likert 1 sampai 5. Nilai jawaban dari setiap responden kemudian dikonversi menjadi skor SUS dengan rentang 0 sampai 100. Semakin tinggi skor yang diperoleh, semakin baik tingkat usability sistem. Berdasarkan acuan pada Bab II, sistem dinyatakan layak apabila memperoleh skor SUS rata-rata minimal 68, yang termasuk kategori acceptable.

Bagian ini tidak boleh diisi secara asumtif. Hasil UAT harus berasal dari pengisian kuesioner oleh pengguna nyata atau expert users yang relevan dengan konteks sistem, misalnya pihak manajemen, staf digitalisasi, atau pengguna internal terkait di PT Palawi Risorsis/Wisata Padusan.

**Caption Tabel 4.xx. Hasil rekapitulasi skor User Acceptance Testing menggunakan System Usability Scale**

| No | Responden | Peran/Jabatan | Total Skor Kontribusi | Skor SUS | Kategori |
|---|---|---|---:|---:|---|
| 1 | [Isi nama/inisial responden 1] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 2 | [Isi nama/inisial responden 2] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 3 | [Isi nama/inisial responden 3] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 4 | [Isi nama/inisial responden 4] | [Isi peran] | [Isi] | [Isi] | [Isi] |
| 5 | [Isi nama/inisial responden 5] | [Isi peran] | [Isi] | [Isi] | [Isi] |
|   | **Rata-rata** |  |  | **[Isi skor rata-rata SUS]** | **[Isi kategori akhir]** |

Narasi yang dapat digunakan setelah tabel di atas adalah sebagai berikut:

“Berdasarkan Tabel 4.xx dapat diketahui bahwa hasil User Acceptance Testing menggunakan metode System Usability Scale memperoleh skor rata-rata sebesar [isi skor rata-rata]. Nilai tersebut berada pada kategori [isi kategori] dan menunjukkan bahwa sistem [dapat/belum dapat] diterima oleh pengguna. Dengan demikian, dari sisi usability, sistem analisis segmentasi seasonality kunjungan Wisata Padusan [sudah memenuhi/belum memenuhi] kriteria kelayakan implementasi yang telah ditetapkan, yaitu skor SUS minimal 68.”

Apabila Anda belum benar-benar melakukan penyebaran kuesioner SUS, maka bagian UAT di Bab IV sebaiknya jangan ditulis sebagai hasil final. Pilihan yang aman secara akademik adalah:

- melakukan UAT sungguhan kepada minimal 5 pengguna terkait, lalu mengisi tabel hasilnya
- atau merevisi Bab III agar evaluasi sistem hanya menyatakan Black Box Testing jika UAT memang tidak jadi dilaksanakan

Apabila subbab ini diletakkan setelah bagian implementasi sistem pada draft Bab IV saat ini, maka penomoran yang disarankan adalah sebagai berikut:

- 4.6 Hasil Implementasi Sistem
- 4.7 Hasil Pengujian Sistem
- 4.7.1 Hasil Pengujian Fungsional (Black Box Testing)
- 4.7.2 Hasil Pengujian Penerimaan Pengguna (User Acceptance Testing)
- 4.8 Pembahasan
- 4.9 Keterbatasan Hasil
