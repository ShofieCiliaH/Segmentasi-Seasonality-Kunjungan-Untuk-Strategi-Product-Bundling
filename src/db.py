from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app_state.json"


def _default_state() -> dict:
    return {
        "users": [],
        "riwayat_analisis": [],
        "counters": {
            "users": 0,
            "riwayat_analisis": 0,
        },
    }


def _read_state() -> dict:
    init_db()
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _write_state(state: dict):
    DB_PATH.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")


def _json_default(value):
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        _write_state(_default_state())


def _next_id(state: dict, bucket: str) -> int:
    state["counters"][bucket] += 1
    return int(state["counters"][bucket])


def seed_default_users():
    default_users = [
        {
            "username": "stafit",
            "password": "Padusan2026!",
            "nama_lengkap": "Staf Internal IT",
            "role": "staf_it",
        },
        {
            "username": "marketing",
            "password": "Padusan2026!",
            "nama_lengkap": "Tim Marketing dan Keuangan",
            "role": "marketing",
        },
    ]

    state = _read_state()
    if state["users"]:
        return

    for user in default_users:
        state["users"].append(
            {
                "id_user": _next_id(state, "users"),
                "username": user["username"],
                "password": generate_password_hash(user["password"]),
                "nama_lengkap": user["nama_lengkap"],
                "role": user["role"],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    _write_state(state)


def fetch_user_by_username(username: str):
    state = _read_state()
    return next((user for user in state["users"] if user["username"] == username), None)


def fetch_user_by_id(user_id: int | None):
    if user_id is None:
        return None
    state = _read_state()
    return next((user for user in state["users"] if user["id_user"] == user_id), None)


def store_analysis(
    *,
    user_id: int,
    jumlah_cluster_k: int,
    silhouette_score: float,
    rekomendasi_k: int,
    summary: str,
    source_name: str,
    source_path: str,
    report_path: str,
    dendrogram_path: str,
    payload: dict,
) -> int:
    state = _read_state()
    history_id = _next_id(state, "riwayat_analisis")
    state["riwayat_analisis"].append(
        {
            "id_riwayat": history_id,
            "id_user": user_id,
            "tanggal_proses": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "jumlah_cluster_k": jumlah_cluster_k,
            "silhouette_score": silhouette_score,
            "rekomendasi_k": rekomendasi_k,
            "keterangan_hasil": summary,
            "sumber_file": source_name,
            "sumber_path": source_path,
            "file_laporan": report_path,
            "file_dendrogram": dendrogram_path,
            "hasil_json": json.dumps(payload, ensure_ascii=True, default=_json_default),
        }
    )
    _write_state(state)
    return history_id


def _join_history(history_row: dict, users: list[dict]) -> dict:
    user = next((item for item in users if item["id_user"] == history_row["id_user"]), None)
    joined = dict(history_row)
    if user:
        joined["nama_lengkap"] = user["nama_lengkap"]
        joined["role"] = user["role"]
    else:
        joined["nama_lengkap"] = "Unknown"
        joined["role"] = "unknown"
    return joined


def fetch_recent_history(limit: int = 50):
    state = _read_state()
    ordered = sorted(
        state["riwayat_analisis"],
        key=lambda item: item["id_riwayat"],
        reverse=True,
    )
    return [_join_history(row, state["users"]) for row in ordered[:limit]]


def fetch_analysis(history_id: int):
    state = _read_state()
    row = next((item for item in state["riwayat_analisis"] if item["id_riwayat"] == history_id), None)
    if row is None:
        return None
    return _join_history(row, state["users"])
