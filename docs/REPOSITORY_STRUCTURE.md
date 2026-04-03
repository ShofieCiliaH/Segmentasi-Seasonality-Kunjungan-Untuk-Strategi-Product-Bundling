# Repository Structure

Dokumen ini menjelaskan organisasi folder utama pada project.

## Root Files

- `app.py`: entry point aplikasi Flask
- `requirements.txt`: daftar dependensi utama
- `README.md`: dokumentasi utama repository
- `CHANGELOG.md`: riwayat perubahan versi
- `.gitignore`: daftar file/folder yang tidak ikut dipublikasikan

## Main Directories

### `src/`

Source code inti aplikasi.

- `db.py`: persistence lokal untuk user dan riwayat analisis
- `services/analysis.py`: preprocessing, clustering, profiling, dan rule generation
- `services/reporting.py`: pembuatan laporan PDF

### `templates/`

Template HTML Flask.

- `login.html`
- `dashboard.html`
- `history.html`
- `history_detail.html`
- `base.html`

### `static/`

Aset antarmuka.

- `css/app.css`: styling dashboard

### `scripts/`

Script bantu untuk pengembangan dan demonstrasi.

- `generate_sample_data.py`: generator sample data sintetis

### `sample_data/`

Data contoh non-sensitif untuk uji aplikasi.

### `docs/`

Dokumentasi tambahan untuk GitHub.

- arsitektur aplikasi
- struktur repository
- release notes

## Ignored Directories

Folder berikut tidak ikut dipublikasikan:

- `data/data-asli/`
- `storage/uploads/`
- `storage/generated/`
- `.vendor/`
- `.venv/`

Tujuannya adalah menjaga repository tetap bersih, ringan, dan tidak membawa data sensitif.
