import logging
from datetime import datetime

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.scheduler import scheduled_ricerca_amazon, scheduled_update, scheduler
from app.core.security import get_current_user
from app.db.database import Base, engine, get_db
from app.models.trackingData import Articolo, Ricerca, RisultatoRicerca, StoricoPrezzo
from app.models.user import User
from app.services.system_service import systemService

# Configurazione semplice che stampa: LIVELLO - NOME_MODULO - MESSAGGIO

logging.basicConfig(level=logging.INFO, format="%(levelname)s: [%(name)s] %(message)s")

logger = logging.getLogger(__name__)
logger.info("Integration-hub avviato con successo")


app = FastAPI(title="Integration Hub API")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router, prefix="/api/v1")
templates = Jinja2Templates(directory="templates")


# Crea le tabelle all'avvio
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database inizializzato.")

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler avviato: i task automatici sono attivi.")

    if not scheduler.get_job("amazon_rotative_task"):
        scheduler.add_job(
            scheduled_ricerca_amazon,
            "interval",
            hours=16,  # <--- 16 ore per non superare le 50 chiamate/mese
            id="amazon_rotative_task",
            misfire_grace_time=3600,
            # next_run_time= datetime.now()
        )
        logger.info("Task rotativo Amazon configurato (1 chiamata ogni 16 ore)")

    if not scheduler.get_job("api_task"):
        scheduler.add_job(
            scheduled_update,
            "interval",
            hours=3,
            id="api_task",
            misfire_grace_time=3600,
        )
        logger.info("Task API Update aggiunto")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("scheduler spento.")


@app.get("/")
def read_root():
    return {"status": "Integration Hub Online on Raspberry Pi 3 model B"}


@app.get("/gui", response_class=HTMLResponse)
async def gui_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    from app.api.routes import get_dashboard

    dashboard_data = await get_dashboard(db)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "data": dashboard_data, "now": datetime.now()},
    )


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    from app.api.routes import get_dashboard

    dashboard_data = await get_dashboard(db)

    system_stats = systemService.get_syst_stats()

    full_data = dashboard_data
    full_data["system"] = system_stats
    # return templates.TemplateResponse("dashboard.html", {"request": request})
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": full_data,
            "now": datetime.now(),
            "user": current_user,
        },
    )
