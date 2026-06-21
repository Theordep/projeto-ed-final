#!/usr/bin/env python3
"""Executa o pipeline SparkEats (Landing → Bronze → Silver → Gold)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STEPS = ("landing", "bronze", "silver", "gold")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline SparkEats — Landing → Bronze → Silver → Gold"
    )
    parser.add_argument(
        "--step",
        choices=STEPS + ("all",),
        default="all",
        help="Etapa a executar",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Carga incremental (landing: tabelas fato; gold: checkpoint fato_pedidos)",
    )
    args = parser.parse_args()

    steps = list(STEPS) if args.step == "all" else [args.step]

    for step in steps:
        if step == "landing":
            from sparkeats.ingestion.landing import run as run_landing

            run_landing(incremental=args.incremental)
        elif step == "bronze":
            from sparkeats.bronze.bronze import run as run_bronze

            run_bronze()
        elif step == "silver":
            from sparkeats.silver.silver import run as run_silver

            run_silver()
        elif step == "gold":
            from sparkeats.gold.gold import run as run_gold

            run_gold(incremental=args.incremental)

    print("\n=== Pipeline finalizado (Landing → Bronze → Silver → Gold) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
