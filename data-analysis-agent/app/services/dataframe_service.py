from __future__ import annotations

import os
import uuid
from pathlib import Path

import pandas as pd
from fastapi import UploadFile

from app.observability.logging import get_logger

logger = get_logger(__name__)


class DataFrameService:
    def __init__(self, base_dir: str | None = None) -> None:
        home = base_dir or os.getenv('DATA_ANALYSIS_AGENT_HOME', './runtime')
        self.base_dir = Path(home)
        self.upload_dir = self.base_dir / 'uploads'
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> tuple[str, Path, pd.DataFrame]:
        dataset_id = f"ds_{uuid.uuid4().hex[:10]}"
        suffix = Path(file.filename or 'dataset.csv').suffix.lower() or '.csv'
        path = self.upload_dir / f"{dataset_id}{suffix}"
        content = await file.read()
        path.write_bytes(content)
        logger.info('dataset.saved dataset_id=%s path=%s', dataset_id, path)
        df = self.load_dataframe(path)
        return dataset_id, path, df

    def path_for_dataset(self, dataset_id: str, filename: str) -> Path:
        suffix = Path(filename).suffix.lower() or '.csv'
        return self.upload_dir / f"{dataset_id}{suffix}"

    def load_dataframe(self, path_or_dataset: str | Path) -> pd.DataFrame:
        path = Path(path_or_dataset)
        suffix = path.suffix.lower()
        if suffix == '.csv':
            return pd.read_csv(path)
        if suffix in {'.xlsx', '.xls'}:
            return pd.read_excel(path)
        raise ValueError(f'Unsupported file type: {suffix}')


dataframe_service = DataFrameService()
