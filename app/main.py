from fastapi import FastAPI
from app.db.database import engine , Base
from app.api.routes import router as api_router


app= FastAPI(title="Integration Hub API")
app.include_router(api_router, prefix="/api/v1")

# Crea le tabelle all'avvio
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"status": "Integration Hub Online on Raspberry Pi 3 model B"}