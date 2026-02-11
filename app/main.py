from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.db.database import engine , Base
from app.api.routes import router as api_router
from app.core.scheduler import scheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from datetime import datetime


app= FastAPI(title="Integration Hub API")
app.include_router(api_router, prefix="/api/v1")
templates =  Jinja2Templates(directory="templates")

# Crea le tabelle all'avvio
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database inizializzato.")

    if not scheduler.running:
        scheduler.start()
        print("Scheduler avviato: i task automatici sono attivi.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("scheduler spento.")
    
@app.get("/")
def read_root():
    return {"status": "Integration Hub Online on Raspberry Pi 3 model B"}

@app.get("/gui", response_class=HTMLResponse)
async def gui_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    from app.api.routes import get_dashboard
    dashboard_data = await get_dashboard(db)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": dashboard_data,
        "now": datetime.now()
    })