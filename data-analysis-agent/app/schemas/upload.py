from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    dataset_id: str = Field(..., description='Unique dataset identifier')
    filename: str
    rows: int
    columns: int
    trace_id: str
