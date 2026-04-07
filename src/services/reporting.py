from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleWarm",
            parent=styles["Title"],
            textColor=colors.HexColor("#1e5077"),
            fontSize=18,
            leading=22,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionWarm",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#24795a"),
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaText",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#35546f"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ExplanationText",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#17344b"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=colors.white,
            wordWrap="CJK",
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#17344b"),
            wordWrap="CJK",
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellCompact",
            parent=styles["BodyText"],
            fontSize=7.6,
            leading=9.4,
            textColor=colors.HexColor("#17344b"),
            wordWrap="CJK",
        )
    )
    return styles


def to_paragraph(value, style):
    text = "" if value is None else str(value)
    safe_text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return Paragraph(safe_text, style)


def build_table(data, *, styles, column_widths=None, compact=False, has_header=True):
    header_style = styles["TableHeader"]
    cell_style = styles["TableCellCompact"] if compact else styles["TableCell"]

    formatted_rows = []
    for row_index, row in enumerate(data):
        style = header_style if has_header and row_index == 0 else cell_style
        formatted_rows.append([to_paragraph(value, style) for value in row])

    table = Table(formatted_rows, colWidths=column_widths, repeatRows=1 if has_header else 0)
    table_styles = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9dcea")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if has_header:
        table_styles.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82b1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fcff")),
            ]
        )
    else:
        table_styles.append(("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fcff")))

    table.setStyle(TableStyle(table_styles))
    return table


def fit_image(image_path: str, max_width: float, max_height: float):
    image = Image(image_path)
    width, height = image.imageWidth, image.imageHeight
    if not width or not height:
        image.drawWidth = max_width
        image.drawHeight = max_height
        return image

    ratio = min(max_width / width, max_height / height)
    image.drawWidth = width * ratio
    image.drawHeight = height * ratio
    return image


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

    styles = make_styles()
    story = [
        Paragraph("Laporan Analisis Strategi Bundling Wisata Padusan", styles["TitleWarm"]),
        Paragraph(
            f"File sumber: <b>{result['source_name']}</b><br/>"
            f"Dibuat oleh: <b>{generated_by}</b><br/>"
            f"Waktu proses: <b>{result['uploaded_at']}</b>",
            styles["MetaText"],
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
        styles=styles,
        column_widths=[4.5 * cm, document.width - (4.5 * cm)],
        compact=True,
        has_header=False,
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.35 * cm))

    if result.get("dendrogram_path"):
        story.append(Paragraph("Visualisasi Dendrogram", styles["SectionWarm"]))
        story.append(fit_image(result["dendrogram_path"], max_width=document.width, max_height=8.2 * cm))
        story.append(Spacer(1, 0.3 * cm))

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
    cluster_table = build_table(
        cluster_rows,
        styles=styles,
        column_widths=[2.1 * cm, 3.2 * cm, 4.7 * cm, 3.1 * cm, 3.4 * cm],
        compact=True,
    )
    story.append(
        KeepTogether(
            [
                Paragraph("Rekomendasi Strategi", styles["SectionWarm"]),
                cluster_table,
                Spacer(1, 0.3 * cm),
            ]
        )
    )

    explanation_blocks = [Paragraph("Penjelasan Rekomendasi", styles["SectionWarm"])]
    for cluster in result["cluster_profiles"]:
        explanation_blocks.append(
            Paragraph(
                f"<b>{cluster['cluster_name']} - {cluster['package_name']}</b><br/>{cluster['recommendation_reason_formal']}",
                styles["ExplanationText"],
            )
        )
    story.append(KeepTogether(explanation_blocks))
    story.append(Spacer(1, 0.2 * cm))

    candidate_rows = [["k", "Silhouette Score"]]
    for candidate in result["candidate_scores"]:
        candidate_rows.append([str(candidate["k"]), str(candidate["score"])])
    candidate_table = build_table(
        candidate_rows,
        styles=styles,
        column_widths=[2.0 * cm, 4.0 * cm],
        compact=True,
    )
    story.append(
        KeepTogether(
            [
                Paragraph("Kandidat Jumlah Cluster", styles["SectionWarm"]),
                candidate_table,
            ]
        )
    )

    document.build(story)
