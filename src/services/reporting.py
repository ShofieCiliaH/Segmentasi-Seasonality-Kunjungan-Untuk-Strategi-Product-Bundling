from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_table(data, column_widths=None):
    table = Table(data, colWidths=column_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c26042")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9b99e")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fffaf4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def generate_report_pdf(*, result: dict, generated_by: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleWarm",
            parent=styles["Title"],
            textColor=colors.HexColor("#7a2e1e"),
            fontSize=20,
            leading=24,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionWarm",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#2f5d50"),
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        )
    )

    story = [
        Paragraph("Laporan Analisis Strategi Bundling Wisata Padusan", styles["TitleWarm"]),
        Paragraph(
            f"File sumber: <b>{result['source_name']}</b><br/>"
            f"Dibuat oleh: <b>{generated_by}</b><br/>"
            f"Waktu proses: <b>{result['uploaded_at']}</b>",
            styles["BodyText"],
        ),
        Spacer(1, 0.35 * cm),
        Paragraph("Ringkasan Eksekusi", styles["SectionWarm"]),
    ]

    summary_table = build_table(
        [
            ["Metode", "Ward + Euclidean Distance + Silhouette"],
            ["Hari dianalisis", str(result["days_analysed"])],
            ["Baris awal", str(result["rows_initial"])],
            ["Baris valid", str(result["rows_cleaned"])],
            ["k rekomendasi", str(result["recommended_k"])],
            ["k aktif", str(result["active_k"])],
            ["Silhouette aktif", str(result["active_silhouette"])],
        ],
        column_widths=[4.5 * cm, 11.2 * cm],
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.35 * cm))

    if result.get("dendrogram_path"):
        story.append(Paragraph("Visualisasi Dendrogram", styles["SectionWarm"]))
        story.append(Image(result["dendrogram_path"], width=17 * cm, height=8 * cm))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Rekomendasi Strategi", styles["SectionWarm"]))
    cluster_rows = [["Cluster", "Segmen", "Profil", "Paket", "Target Waktu"]]
    for cluster in result["cluster_profiles"]:
        cluster_rows.append(
            [
                cluster["cluster_name"],
                cluster["segment_label"],
                cluster["profile_text"],
                cluster["package_name"],
                cluster["target_season"],
            ]
        )
    story.append(
        build_table(
            cluster_rows,
            column_widths=[2.2 * cm, 3.2 * cm, 5.1 * cm, 3.5 * cm, 3.3 * cm],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Kandidat Jumlah Cluster", styles["SectionWarm"]))
    candidate_rows = [["k", "Silhouette Score"]]
    for candidate in result["candidate_scores"]:
        candidate_rows.append([str(candidate["k"]), str(candidate["score"])])
    story.append(build_table(candidate_rows, column_widths=[2.2 * cm, 4.2 * cm]))

    document.build(story)
