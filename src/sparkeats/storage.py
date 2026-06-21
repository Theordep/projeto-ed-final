"""Paths locais (Spark file://) e sync para MinIO."""

from __future__ import annotations

import subprocess
from pathlib import Path

from sparkeats.config import (
    BUCKETS,
    MINIO_ACCESS_KEY,
    MINIO_CONTAINER,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    PROJECT_ROOT,
)

_LAYER_TO_BUCKET = {
    "landing": BUCKETS["landing"],
    "bronze": BUCKETS["bronze"],
    "silver": BUCKETS["silver"],
    "gold": BUCKETS["gold"],
}


def data_root() -> Path:
    """Raiz das camadas. Preferir path Linux (DATA_ROOT) fora de /mnt/c."""
    import os

    return Path(os.getenv("DATA_ROOT", str(Path(PROJECT_ROOT) / "data")))


DATA_ROOT = data_root()
LANDING_ROOT = DATA_ROOT / "landing"


def _local_dir(layer: str) -> Path:
    if layer == "landing":
        return LANDING_ROOT
    return DATA_ROOT / BUCKETS[layer]


def layer_uri(layer: str, table: str) -> str:
    path = _local_dir(layer) / "postgres" / table
    path.mkdir(parents=True, exist_ok=True)
    return path.as_uri()


def landing_csv_glob(table: str) -> str:
    base = LANDING_ROOT / "postgres" / table
    return f"{base.as_uri()}/*/*/*/*/*.csv"


def _sync_via_minio_client(local: Path, bucket: str) -> None:
    from minio import Minio

    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    client = Minio(
        endpoint,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_ENDPOINT.startswith("https"),
    )
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    for path in local.rglob("*"):
        if path.is_file():
            key = path.relative_to(local).as_posix()
            client.fput_object(bucket, key, str(path))
    print(f"  [sync] {local.name} → MinIO/{bucket} OK (minio client)")


def _sync_via_docker_mc(local: Path, bucket: str) -> None:
    network = subprocess.check_output(
        [
            "docker",
            "inspect",
            MINIO_CONTAINER,
            "--format",
            "{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}",
        ],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    if not network:
        raise RuntimeError(f"rede do container {MINIO_CONTAINER} não encontrada")
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            network,
            "-v",
            f"{local.resolve()}:/src",
            "--entrypoint",
            "/bin/sh",
            "minio/mc",
            "-c",
            f"mc alias set l http://minio:9000 {MINIO_ACCESS_KEY} {MINIO_SECRET_KEY} "
            f"&& mc mirror --overwrite /src l/{bucket}",
        ],
        check=True,
        capture_output=True,
    )
    print(f"  [sync] {local.name} → MinIO/{bucket} OK (docker mc)")


def sync_to_minio(layer: str) -> None:
    """Espelha camada local no bucket MinIO."""
    local = _local_dir(layer)
    if not local.exists():
        return
    bucket = _LAYER_TO_BUCKET[layer]
    try:
        _sync_via_minio_client(local, bucket)
    except Exception as exc:
        try:
            _sync_via_docker_mc(local, bucket)
        except (FileNotFoundError, subprocess.CalledProcessError, RuntimeError):
            print(f"  [sync] {layer}: pulado ({exc})")
