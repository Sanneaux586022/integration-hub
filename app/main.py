from fastapi import FastApi
from app.db.database import engine , Base
import asyncio

app= FastApi(title="Integration Hub API")

# Crea le tabelle all'avvio
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"status": "Integration Hub Online on Raspberry Pi 3 model B"}