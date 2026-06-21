#!/usr/bin/env python3
"""Executa o pipeline SparkEats (Landing → Bronze → Silver). Issue #16."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STEPS = ("landing", "bronze", "silver")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline SparkEats — Landing → Bronze → Silver")
    parser.add_argument(
        "--step",
        choices=STEPS + ("all",),
        default="all",
        help="Etapa a executar",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Carga incremental na landing (tabelas fato)",
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

    print("\n=== Pipeline finalizado (Landing → Bronze → Silver) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
