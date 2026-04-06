from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = BASE_DIR / ".vendor"

if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from src.db import (
    fetch_analysis,
    fetch_recent_history,
    fetch_user_by_id,
    fetch_user_by_username,
    init_db,
    seed_default_users,
    store_analysis,
)
from src.services.analysis import AnalysisError, run_analysis
from src.services.reporting import generate_report_pdf

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "padusan-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
REPORT_DIR = STORAGE_DIR / "generated" / "reports"
PLOT_DIR = STORAGE_DIR / "generated" / "plots"

for directory in (UPLOAD_DIR, REPORT_DIR, PLOT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

init_db()
seed_default_users()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def resolve_storage_path(relative_path: str | None) -> Path | None:
    if not relative_path:
        return None
    full_path = (BASE_DIR / relative_path).resolve()
    if not full_path.is_relative_to(STORAGE_DIR.resolve()):
        return None
    return full_path


def file_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return url_for("artifact_file", relpath=relative_path)


def inflate_analysis(record):
    payload = json.loads(record["hasil_json"])
    payload["history_id"] = record["id_riwayat"]
    payload["tanggal_proses"] = record["tanggal_proses"]
    payload["jumlah_cluster_k"] = record["jumlah_cluster_k"]
    payload["silhouette_score"] = record["silhouette_score"]
    payload["recommended_k"] = record["rekomendasi_k"]
    payload["summary"] = record["keterangan_hasil"]
    payload["source_name"] = record["sumber_file"]
    payload["source_path"] = record["sumber_path"]
    payload["report_url"] = file_url(record["file_laporan"])
    payload["plot_url"] = file_url(record["file_dendrogram"])
    payload["analyst_name"] = record["nama_lengkap"]
    payload["role"] = record["role"]
    return payload


def build_summary(cluster_profiles):
    return "; ".join(f"{cluster['cluster_name']}: {cluster['segment_label']}" for cluster in cluster_profiles)


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = fetch_user_by_id(user_id) if user_id else None


@app.context_processor
def inject_globals():
    return {
        "app_name": "Padusan Bundling Intelligence",
        "current_user": g.user,
    }


@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = fetch_user_by_username(username)

        if user is None or not check_password_hash(user["password"], password):
            flash("Username atau password tidak cocok.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id_user"]
        flash("Login berhasil. Anda bisa mulai mengunggah data transaksi.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Sesi Anda sudah ditutup.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    analysis_id = request.args.get("analysis_id", type=int) or session.get("current_analysis_id")
    analysis = None
    if analysis_id:
        record = fetch_analysis(analysis_id)
        if record:
            analysis = inflate_analysis(record)
            session["current_analysis_id"] = analysis_id

    history_preview = [inflate_analysis(row) for row in fetch_recent_history(limit=5)]
    return render_template("dashboard.html", analysis=analysis, history_preview=history_preview)


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    upload = request.files.get("data_file")
    manual_k = request.form.get("manual_k", type=int)
    source_path = None
    source_name = None

    if upload and upload.filename:
        safe_name = secure_filename(upload.filename)
        if not safe_name:
            flash("Nama file tidak valid.", "error")
            return redirect(url_for("dashboard"))

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        stored_name = f"{timestamp}-{safe_name}"
        target_path = UPLOAD_DIR / stored_name
        upload.save(target_path)
        source_path = target_path
        source_name = upload.filename
        session["last_source_path"] = target_path.relative_to(BASE_DIR).as_posix()
        session["last_source_name"] = source_name
    else:
        stored_relpath = request.form.get("source_path") or session.get("last_source_path")
        source_path = resolve_storage_path(stored_relpath)
        source_name = request.form.get("source_name") or session.get("last_source_name")

    if source_path is None or not source_path.exists():
        flash("Unggah file transaksi `.xlsx` atau `.csv` terlebih dahulu.", "error")
        return redirect(url_for("dashboard"))

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
    dendrogram_path = PLOT_DIR / f"dendrogram-{run_id}.png"
    report_path = REPORT_DIR / f"laporan-analisis-{run_id}.pdf"

    try:
        result = run_analysis(
            source_path=source_path,
            source_name=source_name or source_path.name,
            manual_k=manual_k,
            dendrogram_output=dendrogram_path,
        )
        result["dendrogram_path"] = str(dendrogram_path)
        generate_report_pdf(
            result=result,
            generated_by=g.user["nama_lengkap"],
            output_path=report_path,
        )
    except AnalysisError as exc:
        flash(str(exc), "error")
        return redirect(url_for("dashboard"))

    result["report_path"] = report_path.relative_to(BASE_DIR).as_posix()
    result["dendrogram_path"] = dendrogram_path.relative_to(BASE_DIR).as_posix()

    history_id = store_analysis(
        user_id=g.user["id_user"],
        jumlah_cluster_k=result["active_k"],
        silhouette_score=result["active_silhouette"],
        rekomendasi_k=result["recommended_k"],
        summary=build_summary(result["cluster_profiles"]),
        source_name=result["source_name"],
        source_path=source_path.relative_to(BASE_DIR).as_posix(),
        report_path=result["report_path"],
        dendrogram_path=result["dendrogram_path"],
        payload=result,
    )

    session["current_analysis_id"] = history_id
    flash("Analisis berhasil dijalankan dan riwayat sudah disimpan.", "success")
    return redirect(url_for("dashboard", analysis_id=history_id))


@app.route("/history")
@login_required
def history():
    rows = [inflate_analysis(row) for row in fetch_recent_history(limit=100)]
    return render_template("history.html", analyses=rows)


@app.route("/history/<int:history_id>")
@login_required
def history_detail(history_id: int):
    record = fetch_analysis(history_id)
    if record is None:
        abort(404)
    analysis = inflate_analysis(record)
    return render_template("history_detail.html", analysis=analysis)


@app.route("/artifacts/<path:relpath>")
@login_required
def artifact_file(relpath: str):
    file_path = resolve_storage_path(relpath)
    if file_path is None or not file_path.exists():
        abort(404)
    return send_file(file_path)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5050)
