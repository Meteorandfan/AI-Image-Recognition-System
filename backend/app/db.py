import sqlite3
from pathlib import Path
from typing import List, Optional
from .schemas import PredictResult


# 初始化数据库与表结构

def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()

    # 兼容旧表结构：没有 stored_name 字段时进行补齐
    cursor.execute("PRAGMA table_info(history)")
    columns = [row[1] for row in cursor.fetchall()]
    if "stored_name" not in columns:
        cursor.execute("ALTER TABLE history ADD COLUMN stored_name TEXT NOT NULL DEFAULT ''")
        conn.commit()

    conn.close()


# 写入记录

def save_history(
    db_path: Path,
    filename: str,
    stored_name: str,
    label: str,
    confidence: float,
    created_at: str,
) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (filename, stored_name, label, confidence, created_at) VALUES (?, ?, ?, ?, ?)",
        (filename, stored_name, label, confidence, created_at),
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


# 读取全部记录

def fetch_all_history(db_path: Path) -> List[PredictResult]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, label, confidence, created_at FROM history ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        PredictResult(
            id=row[0],
            filename=row[1],
            label=row[2],
            confidence=row[3],
            created_at=row[4],
        )
        for row in rows
    ]


# 获取存储文件名

def fetch_stored_name(db_path: Path, record_id: int) -> Optional[str]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT stored_name FROM history WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# 删除指定记录

def delete_history(db_path: Path, record_id: int) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0
