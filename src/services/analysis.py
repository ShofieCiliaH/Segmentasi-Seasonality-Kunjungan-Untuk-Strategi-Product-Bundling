from __future__ import annotations

import io
import math
import re
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler


class AnalysisError(Exception):
    """Raised when the uploaded dataset cannot be analysed safely."""


HEADER_ALIASES = {
    "tanggal": {"tanggal", "tgl", "tanggaltransaksi", "date"},
    "lokasi_wisata": {"lokasiwisata", "lokasi", "unit", "unitwisata"},
    "jenis_tiket": {"jenistiket", "kategori", "jenislayanan"},
    "nama_tiket": {"namatiket", "namaproduk", "produk", "namaitem", "tiket"},
    "jumlah": {"jumlah", "qty", "kuantitas", "jumlahjual", "quantity"},
}

PRIMARY_CATEGORIES = [
    "Tiket Masuk",
    "Parkir",
    "Wahana Air",
    "Akomodasi",
    "De Qoem (VIP)",
]


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def parse_numeric(value) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Rp", "").replace("rp", "").replace(" ", "")
    text = text.replace(".", "")
    text = text.replace(",", ".")
    text = re.sub(r"[^0-9\-.]", "", text)
    if text in {"", "-", ".", "-.", ".-"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def resolve_columns(df: pd.DataFrame) -> dict[str, str]:
    mapping = {}
    normalized_map = {normalize_header(column): column for column in df.columns}
    for canonical, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized_map:
                mapping[canonical] = normalized_map[alias]
                break

    required = {"tanggal", "nama_tiket", "jumlah"}
    missing = sorted(required - set(mapping))
    if missing:
        raise AnalysisError(
            "Kolom wajib tidak ditemukan: "
            + ", ".join(missing)
            + ". Pastikan file memuat minimal kolom Tanggal, Nama Tiket, dan Jumlah."
        )
    return mapping


def categorize_product(name: str, jenis_tiket: str = "") -> str:
    normalized_name = str(name).lower()
    normalized_kind = str(jenis_tiket).lower()

    if any(keyword in normalized_name for keyword in ("dqoem", "de qoem", "d'qoem", "dqom")):
        return "De Qoem (VIP)"

    if any(
        keyword in normalized_name
        for keyword in (
            "camp",
            "cabin",
            "glamping",
            "pinus",
            "flamboyan",
            "penginapan",
            "resort",
            "onsen",
            "stay",
            "bobocabin",
            "soemo",
            "jungle",
        )
    ):
        return "Akomodasi"

    if "kendaraan" in normalized_kind or any(
        keyword in normalized_name for keyword in ("parkir", "roda 2", "roda 4", "roda 6", "r2", "r4", "r6")
    ):
        return "Parkir"

    if "ktm" in normalized_kind or any(
        keyword in normalized_name
        for keyword in ("tiket masuk", "weekend", "weekday", "dewasa", "anak", "reguler")
    ):
        if "whirlpool" not in normalized_name and "kolam" not in normalized_name:
            return "Tiket Masuk"

    if "wahana" in normalized_kind or any(
        keyword in normalized_name
        for keyword in ("whirlpool", "kolam", "gambiran", "air panas", "therapy", "terapi")
    ):
        return "Wahana Air"

    return "Lainnya"


def demand_level(value: float) -> str:
    if value >= 0.66:
        return "tinggi"
    if value >= 0.33:
        return "sedang"
    return "rendah"


def build_profile_text(row: dict, weekend_share: float) -> str:
    snippets = []
    for field, label in (
        ("Tiket Masuk", "tiket masuk"),
        ("Parkir", "parkir"),
        ("Wahana Air", "wahana air"),
        ("Akomodasi", "akomodasi"),
        ("De Qoem (VIP)", "layanan VIP"),
    ):
        if field in row:
            snippets.append(f"{label} {demand_level(row[field])}")

    day_pattern = "didominasi akhir pekan" if weekend_share >= 0.5 else "cenderung tersebar di hari kerja"
    return ", ".join(snippets[:4]) + f", serta {day_pattern}."


def infer_segment(row: dict, weekend_share: float) -> tuple[str, str, str, str]:
    tiket = row.get("Tiket Masuk", 0.0)
    parkir = row.get("Parkir", 0.0)
    wahana = row.get("Wahana Air", 0.0)
    akomodasi = row.get("Akomodasi", 0.0)
    vip = row.get("De Qoem (VIP)", 0.0)
    overall = (tiket + parkir + wahana + akomodasi) / 4

    if tiket > 0.55 and parkir > 0.45 and wahana > 0.55:
        return (
            "High Season / Peak Days",
            "Paket Terusan Wahana Air",
            "Tiket Masuk + Wahana Kolam",
            "Libur nasional, libur sekolah, cuti bersama",
        )

    if akomodasi > 0.55 or (akomodasi > 0.4 and weekend_share >= 0.55):
        return (
            "Staycation / Weekend Pattern",
            "Paket Camping Adventure",
            "Tiket Masuk + Akomodasi",
            "Akhir pekan reguler (Sabtu-Minggu)",
        )

    if vip > 0.55:
        return (
            "Premium Wellness Pattern",
            "Paket Premium Onsen",
            "Tiket Masuk + De Qoem (VIP)",
            "Hari khusus dengan minat layanan privat",
        )

    if overall <= 0.35:
        return (
            "Low Season / Weekday",
            "Paket Hemat Weekday",
            "Tiket Masuk + Parkir",
            "Hari kerja biasa dengan demand rendah",
        )

    return (
        "Mixed Leisure Pattern",
        "Paket Fleksibel Keluarga",
        "Tiket Masuk + Wahana Air + Parkir",
        "Hari ramai sedang dengan karakter campuran",
    )


def get_segment_descriptions(segment_label: str) -> tuple[str, str]:
    descriptions = {
        "High Season / Peak Days": (
            "Cluster ini menunjukkan intensitas kunjungan yang tinggi, terutama pada tiket masuk, parkir, dan wahana air. Oleh karena itu, sistem merekomendasikan Paket Terusan Wahana Air untuk memaksimalkan transaksi pada periode ramai.",
            "Berdasarkan profil cluster, permintaan pada kategori tiket masuk, parkir, dan wahana air berada pada tingkat tinggi. Kondisi ini menunjukkan adanya periode kunjungan puncak, sehingga sistem merekomendasikan Paket Terusan Wahana Air sebagai strategi bundling yang paling sesuai. Rekomendasi ini ditujukan untuk mengoptimalkan nilai transaksi pada saat volume kunjungan sedang tinggi.",
        ),
        "Staycation / Weekend Pattern": (
            "Cluster ini menunjukkan dominasi layanan akomodasi dan cenderung terkait dengan aktivitas akhir pekan. Oleh karena itu, sistem merekomendasikan Paket Camping Adventure karena lebih sesuai dengan pola kunjungan berbasis pengalaman menginap.",
            "Berdasarkan hasil profiling, cluster ini memiliki kecenderungan kuat pada kategori akomodasi dan menunjukkan pola kunjungan yang mengarah pada akhir pekan. Dengan karakteristik tersebut, sistem merekomendasikan Paket Camping Adventure karena kombinasi tiket masuk dan akomodasi dinilai paling sesuai dengan kebutuhan pengunjung pada cluster ini. Strategi ini diarahkan untuk mendukung kunjungan bertema staycation atau rekreasi akhir pekan.",
        ),
        "Premium Wellness Pattern": (
            "Cluster ini menunjukkan minat yang lebih tinggi pada layanan VIP atau premium wellness. Oleh karena itu, sistem merekomendasikan Paket Premium Onsen untuk menyesuaikan strategi bundling dengan preferensi layanan privat dan eksklusif.",
            "Cluster ini ditandai oleh dominasi layanan De Qoem (VIP), yang menunjukkan adanya kecenderungan permintaan terhadap pengalaman wisata yang lebih privat dan premium. Berdasarkan kondisi tersebut, sistem merekomendasikan Paket Premium Onsen sebagai strategi bundling yang paling relevan. Rekomendasi ini ditujukan untuk menyesuaikan penawaran dengan preferensi pengunjung yang mencari layanan eksklusif.",
        ),
        "Low Season / Weekday": (
            "Cluster ini menunjukkan tingkat permintaan yang relatif rendah pada kategori utama. Oleh karena itu, sistem merekomendasikan Paket Hemat Weekday untuk membantu mendorong minat kunjungan pada periode permintaan rendah.",
            "Berdasarkan profil cluster, permintaan pada kategori utama seperti tiket masuk, parkir, dan wahana air berada pada tingkat relatif rendah. Kondisi ini menunjukkan periode kunjungan yang lebih sepi, sehingga sistem merekomendasikan Paket Hemat Weekday sebagai strategi bundling yang lebih sederhana dan efisien. Rekomendasi ini bertujuan untuk meningkatkan daya tarik kunjungan pada periode permintaan rendah.",
        ),
        "Mixed Leisure Pattern": (
            "Cluster ini menunjukkan pola kunjungan yang campuran dan tidak didominasi oleh satu kategori layanan tertentu. Oleh karena itu, sistem merekomendasikan Paket Fleksibel Keluarga agar penawaran tetap relevan untuk kebutuhan pengunjung yang beragam.",
            "Cluster ini menunjukkan karakteristik permintaan yang bersifat campuran, tanpa dominasi yang sangat kuat pada satu kategori layanan tertentu. Dengan pola tersebut, sistem merekomendasikan Paket Fleksibel Keluarga sebagai strategi bundling yang lebih adaptif terhadap variasi kebutuhan pengunjung. Rekomendasi ini ditujukan untuk menjaga relevansi penawaran pada kondisi permintaan yang heterogen.",
        ),
    }
    fallback = (
        "Cluster ini menghasilkan rekomendasi bundling berdasarkan profil kunjungan yang terbentuk dari data historis.",
        "Cluster ini menghasilkan rekomendasi bundling berdasarkan profil kunjungan yang terbentuk dari data historis, sehingga strategi yang disarankan mengikuti pola aktual dalam data.",
    )
    return descriptions.get(segment_label, fallback)


def calculate_cut_height(linkage_matrix, cluster_count: int) -> float | None:
    total_samples = linkage_matrix.shape[0] + 1
    if cluster_count <= 1 or cluster_count > total_samples:
        return None
    distances = linkage_matrix[:, 2]
    upper_index = total_samples - cluster_count
    lower_index = upper_index - 1

    lower = distances[lower_index] if lower_index >= 0 else 0.0
    upper = distances[upper_index] if upper_index < len(distances) else distances[-1]
    if upper <= lower:
        return float(upper)
    return float(lower + ((upper - lower) / 2))


def render_dendrogram(matrix: pd.DataFrame, linkage_matrix, cluster_count: int, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = [index.strftime("%d-%m-%Y") for index in matrix.index]
    no_labels = len(labels) > 60
    figure_height = max(6, min(14, len(labels) / 7))

    fig, ax = plt.subplots(figsize=(14, figure_height))
    dendrogram(
        linkage_matrix,
        labels=None if no_labels else labels,
        leaf_rotation=90,
        leaf_font_size=8,
        color_threshold=None,
        ax=ax,
    )
    cut_height = calculate_cut_height(linkage_matrix, cluster_count)
    if cut_height is not None:
        ax.axhline(
            y=cut_height,
            color="#b55d3d",
            linestyle="--",
            linewidth=2,
            label=f"Cut-off k={cluster_count}",
        )
        ax.legend(loc="upper right")

    ax.set_title("Dendrogram Agglomerative Hierarchical Clustering", fontsize=14, fontweight="bold")
    ax.set_xlabel("Hari Operasional")
    ax.set_ylabel("Jarak Ward")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def compute_outlier_summary(matrix: pd.DataFrame) -> list[dict]:
    summaries = []
    for column in matrix.columns:
        series = matrix[column]
        if series.nunique() <= 1:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - (1.5 * iqr)
        upper = q3 + (1.5 * iqr)
        flagged = series[(series < lower) | (series > upper)]
        if flagged.empty:
            continue
        examples = [
            {
                "tanggal": index.strftime("%Y-%m-%d"),
                "nilai": int(value),
            }
            for index, value in flagged.head(3).items()
        ]
        summaries.append(
            {
                "kategori": column,
                "jumlah_outlier": int(flagged.shape[0]),
                "contoh": examples,
            }
        )
    return summaries


def serialize_frame(frame: pd.DataFrame, limit: int = 10) -> list[dict]:
    preview = frame.head(limit).copy()
    preview = preview.reset_index()
    preview.columns = [str(column) for column in preview.columns]

    records = []
    for record in preview.to_dict(orient="records"):
        cleaned = {}
        for key, value in record.items():
            if hasattr(value, "strftime"):
                cleaned[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, float) and math.isnan(value):
                cleaned[key] = None
            elif isinstance(value, float):
                cleaned[key] = round(value, 4)
            else:
                cleaned[key] = value
        records.append(cleaned)
    return records


def cluster_and_profile(raw_matrix: pd.DataFrame, normalized_matrix: pd.DataFrame, cluster_count: int):
    labels = fcluster(
        linkage(normalized_matrix.values, method="ward"),
        t=cluster_count,
        criterion="maxclust",
    ).tolist()

    temp = pd.DataFrame(
        {
            "label": labels,
            "overall": raw_matrix.sum(axis=1).values,
        },
        index=raw_matrix.index,
    )
    order = (
        temp.groupby("label")["overall"]
        .mean()
        .sort_values(ascending=False)
        .index
        .tolist()
    )
    label_map = {old_label: new_label for new_label, old_label in enumerate(order, start=1)}
    labels = [label_map[label] for label in labels]

    silhouette = round(float(silhouette_score(normalized_matrix.values, labels)), 4)

    assignments = pd.DataFrame({"cluster": labels}, index=raw_matrix.index)
    combined = normalized_matrix.join(assignments)

    profiles = []
    for cluster_id in sorted(assignments["cluster"].unique()):
        cluster_rows = combined[combined["cluster"] == cluster_id].drop(columns="cluster")
        centroid = cluster_rows.mean().to_dict()

        cluster_dates = assignments[assignments["cluster"] == cluster_id].index
        weekend_share = round(
            sum(1 for date in cluster_dates if date.weekday() >= 5) / len(cluster_dates),
            4,
        )

        segment_label, package_name, package_components, target_season = infer_segment(centroid, weekend_share)
        recommendation_reason_short, recommendation_reason_formal = get_segment_descriptions(segment_label)
        profile_text = build_profile_text(centroid, weekend_share)
        dominant_features = [
            field
            for field, score in sorted(centroid.items(), key=lambda item: item[1], reverse=True)
            if score >= 0.33
        ]

        profiles.append(
            {
                "cluster_id": cluster_id,
                "cluster_name": f"Cluster {cluster_id}",
                "segment_label": segment_label,
                "package_name": package_name,
                "package_components": package_components,
                "target_season": target_season,
                "profile_text": profile_text,
                "recommendation_reason_short": recommendation_reason_short,
                "recommendation_reason_formal": recommendation_reason_formal,
                "dominant_features": dominant_features[:3],
                "weekend_share": weekend_share,
                "day_count": int(len(cluster_dates)),
                "date_span": f"{cluster_dates.min().strftime('%d %b %Y')} - {cluster_dates.max().strftime('%d %b %Y')}",
                "centroid": {key: round(float(value), 4) for key, value in centroid.items()},
            }
        )

    return labels, profiles, silhouette


def evaluate_candidates(normalized_matrix: pd.DataFrame):
    sample_count = normalized_matrix.shape[0]
    max_clusters = min(6, sample_count - 1)
    if max_clusters < 2:
        raise AnalysisError("Data harian yang valid belum cukup untuk membentuk klaster. Minimal diperlukan 3 hari data.")

    scores = []
    full_linkage = linkage(normalized_matrix.values, method="ward")
    for cluster_count in range(2, max_clusters + 1):
        labels = fcluster(full_linkage, t=cluster_count, criterion="maxclust")
        if len(set(labels)) < 2:
            continue
        score = round(float(silhouette_score(normalized_matrix.values, labels)), 4)
        scores.append({"k": cluster_count, "score": score})

    if not scores:
        raise AnalysisError("Sistem gagal menemukan konfigurasi jumlah klaster yang valid.")

    recommended = max(scores, key=lambda item: item["score"])["k"]
    return scores, recommended


def repair_xlsx_styles(source_path: Path) -> io.BytesIO | None:
    try:
        with ZipFile(source_path, "r") as source_archive:
            if "xl/styles.xml" not in source_archive.namelist():
                return None

            repaired_stream = io.BytesIO()
            repaired = False
            with ZipFile(repaired_stream, "w", compression=ZIP_DEFLATED) as target_archive:
                for item in source_archive.infolist():
                    payload = source_archive.read(item.filename)
                    if item.filename == "xl/styles.xml":
                        styles_xml = payload.decode("utf-8", errors="replace")
                        updated_xml = styles_xml.replace(
                            "<fill/>",
                            '<fill><patternFill patternType="gray125"/></fill>',
                        )
                        if updated_xml != styles_xml:
                            repaired = True
                            payload = updated_xml.encode("utf-8")
                    target_archive.writestr(item, payload)

            if not repaired:
                return None

            repaired_stream.seek(0)
            return repaired_stream
    except BadZipFile:
        return None


def load_dataset(source_path: Path) -> pd.DataFrame:
    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(source_path)
        except Exception as exc:
            raise AnalysisError(
                "File CSV tidak dapat dibaca. Pastikan format file valid dan tidak sedang rusak."
            ) from exc
    if suffix in {".xlsx", ".xlsm"}:
        try:
            return pd.read_excel(source_path)
        except Exception as exc:
            message = str(exc)
            if "openpyxl.styles.fills.Fill" in message or "Fill() takes no arguments" in message:
                repaired_stream = repair_xlsx_styles(source_path)
                if repaired_stream is not None:
                    try:
                        return pd.read_excel(repaired_stream)
                    except Exception as repaired_exc:
                        raise AnalysisError(
                            "File Excel berhasil dideteksi, tetapi format style workbook rusak sehingga data tetap tidak bisa dibaca. "
                            "Silakan simpan ulang file tersebut sebagai .xlsx atau ekspor ke .csv lalu unggah kembali."
                        ) from repaired_exc

                raise AnalysisError(
                    "File Excel tidak dapat dibaca karena format style workbook rusak. "
                    "Silakan simpan ulang file tersebut sebagai .xlsx atau ekspor ke .csv lalu unggah kembali."
                ) from exc

            raise AnalysisError(
                "File Excel tidak dapat dibaca. Pastikan file valid, tidak sedang terbuka/korup, dan berformat .xlsx."
            ) from exc
    raise AnalysisError("Format file belum didukung. Gunakan `.xlsx` atau `.csv`.")


def run_analysis(*, source_path: Path, source_name: str, manual_k: int | None, dendrogram_output: Path) -> dict:
    raw_df = load_dataset(source_path)
    if raw_df.empty:
        raise AnalysisError("File tidak berisi data transaksi.")

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

    initial_rows = int(working_df.shape[0])
    working_df["tanggal"] = pd.to_datetime(working_df["tanggal"], dayfirst=True, errors="coerce")
    working_df["nama_tiket"] = working_df["nama_tiket"].astype(str).str.strip()
    working_df["jumlah"] = working_df["jumlah"].apply(parse_numeric)
    working_df["jenis_tiket"] = working_df["jenis_tiket"].astype(str).fillna("")

    cleaned_df = working_df.copy()
    stats = Counter()

    invalid_dates = cleaned_df["tanggal"].isna()
    stats["invalid_date"] = int(invalid_dates.sum())
    cleaned_df = cleaned_df[~invalid_dates]

    missing_name = cleaned_df["nama_tiket"].isin({"", "nan", "None"})
    stats["missing_name"] = int(missing_name.sum())
    cleaned_df = cleaned_df[~missing_name]

    missing_quantity = cleaned_df["jumlah"].isna()
    stats["missing_quantity"] = int(missing_quantity.sum())
    cleaned_df = cleaned_df[~missing_quantity]

    zero_quantity = cleaned_df["jumlah"] == 0
    stats["zero_quantity"] = int(zero_quantity.sum())
    cleaned_df = cleaned_df[~zero_quantity]

    negative_quantity = cleaned_df["jumlah"] < 0
    stats["negative_quantity"] = int(negative_quantity.sum())
    cleaned_df = cleaned_df[~negative_quantity]

    normalized_name = cleaned_df["nama_tiket"].str.lower()
    invalid_keyword = normalized_name.str.contains(r"sharing|fix|mitra", regex=True)
    sewa_non_vip = normalized_name.str.contains("sewa", regex=False) & ~normalized_name.str.contains(
        r"dqoem|de qoem|d'qoem",
        regex=True,
    )
    removed_keywords = invalid_keyword | sewa_non_vip
    stats["invalid_keywords"] = int(removed_keywords.sum())
    cleaned_df = cleaned_df[~removed_keywords]

    if cleaned_df.empty:
        raise AnalysisError("Setelah pembersihan data, tidak ada transaksi valid yang tersisa untuk dianalisis.")

    cleaned_df["jumlah"] = cleaned_df["jumlah"].round().astype(int)
    cleaned_df["kategori_produk"] = cleaned_df.apply(
        lambda row: categorize_product(row["nama_tiket"], row["jenis_tiket"]),
        axis=1,
    )

    filtered_df = cleaned_df[cleaned_df["kategori_produk"] != "Lainnya"].copy()
    stats["uncategorized"] = int((cleaned_df["kategori_produk"] == "Lainnya").sum())

    if filtered_df.empty:
        raise AnalysisError("Tidak ada baris data yang berhasil dipetakan ke kategori produk utama.")

    daily_matrix = (
        filtered_df.groupby(["tanggal", "kategori_produk"])["jumlah"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
    )

    for category in PRIMARY_CATEGORIES:
        if category not in daily_matrix.columns:
            daily_matrix[category] = 0

    daily_matrix = daily_matrix[sorted(daily_matrix.columns)]
    if daily_matrix.shape[0] < 3:
        raise AnalysisError("Jumlah hari operasional valid kurang dari 3, sehingga analisis klaster belum layak dijalankan.")

    outlier_summary = compute_outlier_summary(daily_matrix)

    scaler = MinMaxScaler()
    normalized_values = scaler.fit_transform(daily_matrix.values)
    normalized_matrix = pd.DataFrame(
        normalized_values,
        index=daily_matrix.index,
        columns=daily_matrix.columns,
    )

    candidate_scores, recommended_k = evaluate_candidates(normalized_matrix)
    active_k = manual_k or recommended_k
    allowed_values = [item["k"] for item in candidate_scores]
    if active_k not in allowed_values:
        raise AnalysisError(
            f"Jumlah cluster harus berada pada rentang {min(allowed_values)}-{max(allowed_values)} berdasarkan jumlah hari yang tersedia."
        )

    linkage_matrix = linkage(normalized_matrix.values, method="ward")
    labels, cluster_profiles, active_silhouette = cluster_and_profile(daily_matrix, normalized_matrix, active_k)
    render_dendrogram(normalized_matrix, linkage_matrix, active_k, dendrogram_output)

    assignment_rows = []
    for tanggal, label in zip(daily_matrix.index, labels, strict=False):
        assignment_rows.append(
            {
                "tanggal": tanggal.strftime("%Y-%m-%d"),
                "cluster": int(label),
                "hari": tanggal.strftime("%A"),
                "is_weekend": tanggal.weekday() >= 5,
            }
        )

    return {
        "source_name": source_name,
        "uploaded_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows_initial": initial_rows,
        "rows_cleaned": int(filtered_df.shape[0]),
        "days_analysed": int(daily_matrix.shape[0]),
        "candidate_scores": candidate_scores,
        "recommended_k": recommended_k,
        "active_k": active_k,
        "active_silhouette": active_silhouette,
        "categories": daily_matrix.columns.tolist(),
        "cleaning_summary": {
            "invalid_date": stats["invalid_date"],
            "missing_name": stats["missing_name"],
            "missing_quantity": stats["missing_quantity"],
            "zero_quantity": stats["zero_quantity"],
            "negative_quantity": stats["negative_quantity"],
            "invalid_keywords": stats["invalid_keywords"],
            "uncategorized": stats["uncategorized"],
        },
        "outlier_summary": outlier_summary,
        "cluster_profiles": cluster_profiles,
        "daily_assignments": assignment_rows,
        "raw_preview": serialize_frame(filtered_df[["tanggal", "nama_tiket", "kategori_produk", "jumlah"]]),
        "matrix_preview": serialize_frame(daily_matrix),
    }
