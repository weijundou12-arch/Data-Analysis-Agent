from fastapi import FastAPI

from app.api.routes_analyze import router as analyze_router
from app.api.routes_export import router as export_router
from app.api.routes_upload import router as upload_router
from app.observability.logging import configure_logging

configure_logging()

app = FastAPI(
    title='Data Analysis Agent',
    version='0.1.0',
    description='Tool-driven tabular analysis and report generation service.',
)

app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(export_router)


@app.get('/health', tags=['health'])
def health() -> dict:
    return {'status': 'ok'}
