from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import shutil
from typing import Iterable

import pandas as pd

DEFAULT_TARGET_MB = 40
_ORIGINAL_TO_CSV = pd.DataFrame.to_csv


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_chunked_csv(
    df: pd.DataFrame,
    csv_path: str | Path,
    *,
    index: bool = False,
    target_mb: int = DEFAULT_TARGET_MB,
    compression_level: int = 6,
) -> Path:
    """Persist a DataFrame as ordered gzip CSV parts plus a manifest.

    The row count per part is estimated from a UTF-8 CSV sample so each part is
    comfortably below GitHub's 100 MB per-file limit even before gzip
    compression. The original ``foo.csv`` is represented by ``foo_parts/`` and
    ``foo.manifest.json``.
    """
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    stem = csv_path.stem
    parts_dir = csv_path.parent / f'{stem}_parts'
    manifest_path = csv_path.parent / f'{stem}.manifest.json'

    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    parts_dir.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        csv_path.unlink()

    n_rows = len(df)
    if n_rows:
        sample_n = min(20_000, n_rows)
        sample = _ORIGINAL_TO_CSV(df.iloc[:sample_n], None, index=index)
        bytes_per_row = max(1.0, len(sample.encode('utf-8')) / sample_n)
        rows_per_part = max(1, int(target_mb * 1024 * 1024 / bytes_per_row))
    else:
        rows_per_part = 1

    parts: list[dict] = []
    n_parts = max(1, math.ceil(n_rows / rows_per_part)) if n_rows else 1
    for i in range(n_parts):
        start = i * rows_per_part
        stop = min((i + 1) * rows_per_part, n_rows)
        chunk = df.iloc[start:stop]
        filename = f'{stem}.part-{i:04d}.csv.gz'
        path = parts_dir / filename
        _ORIGINAL_TO_CSV(
            chunk,
            path,
            index=index,
            compression={'method': 'gzip', 'compresslevel': compression_level, 'mtime': 0},
        )
        size_bytes = path.stat().st_size
        if size_bytes >= 95 * 1024 * 1024:
            raise RuntimeError(
                f'Chunk {path} is {size_bytes / 1024 / 1024:.1f} MB; '
                'reduce target_mb before committing.'
            )
        parts.append({
            'file': f'{parts_dir.name}/{filename}',
            'row_start': start,
            'row_stop_exclusive': stop,
            'rows': len(chunk),
            'bytes': size_bytes,
            'sha256': _sha256(path),
        })

    manifest = {
        'format': 'chunked_csv_gzip_v1',
        'logical_filename': csv_path.name,
        'compression': 'gzip',
        'index_written': bool(index),
        'target_uncompressed_mb': target_mb,
        'total_rows': n_rows,
        'columns': [str(c) for c in df.columns],
        'parts': parts,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest_path


def read_chunked_csv(manifest_path: str | Path, **read_csv_kwargs) -> pd.DataFrame:
    """Reconstruct a DataFrame written by :func:`write_chunked_csv`."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    frames = [
        pd.read_csv(manifest_path.parent / part['file'], **read_csv_kwargs)
        for part in manifest['parts']
    ]
    if not frames:
        return pd.DataFrame(columns=manifest.get('columns', []))
    return pd.concat(frames, ignore_index=True)


def iter_chunked_csv(manifest_path: str | Path, **read_csv_kwargs) -> Iterable[pd.DataFrame]:
    """Yield ordered chunks without loading the full dataset into memory."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for part in manifest['parts']:
        yield pd.read_csv(manifest_path.parent / part['file'], **read_csv_kwargs)
