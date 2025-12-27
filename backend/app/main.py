from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="CREAM API",
    description="Personal finance tracker API",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
