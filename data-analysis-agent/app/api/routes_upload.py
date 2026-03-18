from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.observability.tracing import new_trace_id
from app.schemas.upload import UploadResponse
from app.services.cache_service import cache
from app.services.dataframe_service import dataframe_service

router = APIRouter(prefix='/upload', tags=['upload'])


@router.post('', response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)) -> UploadResponse:
    trace_id = new_trace_id()
    dataset_id, path, df = await dataframe_service.save_upload(file)
    cache.set_dataset(
        dataset_id,
        {
            'dataset_id': dataset_id,
            'filename': file.filename,
            'path': str(path),
            'rows': int(df.shape[0]),
            'columns': int(df.shape[1]),
            'trace_id': trace_id,
        },
    )
    return UploadResponse(
        dataset_id=dataset_id,
        filename=file.filename or path.name,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        trace_id=trace_id,
    )
