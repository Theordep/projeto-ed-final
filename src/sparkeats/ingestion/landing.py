"""Extrai tabelas PostgreSQL e grava CSV local + MinIO (Landing)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import create_engine, text

from sparkeats.config import INCREMENTAL_TABLES, OLTP_TABLES, sqlalchemy_url
from sparkeats.storage import LANDING_ROOT, sync_to_minio

LANDING_DIR = LANDING_ROOT

_PK_BY_TABLE = {
    "pedidos": "id_pedido",
    "itens_pedido": "id_item_pedido",
    "pagamentos": "id_pagamento",
    "avaliacoes": "id_avaliacao",
}


def extract_table(
    engine,
    table: str,
    incremental: bool = False,
    run_ts: str | None = None,
) -> int:
    run_ts = run_ts or datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
    checkpoint_file = LANDING_DIR / "postgres" / table / "_checkpoint" / "last_id.txt"
    last_id = 0
    if incremental and checkpoint_file.exists():
        last_id = int(checkpoint_file.read_text().strip())

    if incremental and table in INCREMENTAL_TABLES:
        pk = _PK_BY_TABLE[table]
        query = f"SELECT * FROM {table} WHERE {pk} > {last_id} ORDER BY {pk}"
    else:
        query = f"SELECT * FROM {table}"

    df = pd.read_sql(text(query), engine)
    if df.empty and incremental:
        print(f"  [landing] {table}: nenhum registro novo")
        return 0

    out_dir = LANDING_DIR / "postgres" / table / run_ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{table}.csv"
    df.to_csv(out_file, index=False)

    if incremental and table in INCREMENTAL_TABLES and not df.empty:
        pk = _PK_BY_TABLE[table]
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_file.write_text(str(int(df[pk].max())))

    print(f"  [landing] {table}: {len(df)} linhas → {out_file}")
    return len(df)


def upload_to_minio() -> None:
    sync_to_minio("landing")


def run(incremental: bool = False) -> None:
    print("=== Landing: PostgreSQL → CSV (local + MinIO) ===")
    engine = create_engine(sqlalchemy_url())
    run_ts = datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
    total = 0
    for table in OLTP_TABLES:
        total += extract_table(engine, table, incremental=incremental, run_ts=run_ts)
    upload_to_minio()
    print(f"Landing concluída. Total linhas exportadas: {total}")


if __name__ == "__main__":
    import sys

    run(incremental="--incremental" in sys.argv)
