from app.core.config import settings
from app.models.trackingData import Articolo, StoricoPrezzo, Ricerca, RisultatoRicerca
from sqlalchemy import select
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Dict
import  asyncio
import logging

logger = logging.getLogger(__name__)


class AmazonTrackingService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.api_client = AmazonApiclient(settings.AXESSO_BASE_URL, settings.AXESSO_API_KEY)
        self.repo = AmazonRepository(db_session)

    
    async def get_risultati_articoli(self, keyword: str):
        # final_response  = []
        logger.info("INIZIO JOB DI AMAZON")

        risultati_api, asin_list = await self.api_client.fetch_from_api(key_word=keyword)
        art_esistenti = await self.repo.get_articoli_esistenti(asin_list)

        try:
            ricerca = await self.repo.inserisci_ricerca(keyword)

            list_bulk_storico = []
            list_bulk_risultato_ricerca = []

            for posizione, res in enumerate(risultati_api):
                asin_art = res.get("asin")
                prezzo_raw = res.get("price")
                titolo_art = res.get("productDescription", "")

                articolo = art_esistenti.get(asin_art)
                if not articolo:
                    articolo = await self.repo.crea_articolo(asin_art, titolo_art)
                
                try:
                    prezzo_float = float(prezzo_raw) if prezzo_raw else None
                except (ValueError, TypeError):
                    prezzo_float = None

                if prezzo_float is not None:
                    list_bulk_storico.append(StoricoPrezzo(
                        articolo_id = articolo.id,
                        prezzo = prezzo_float
                    ))
                    list_bulk_risultato_ricerca.append(RisultatoRicerca(
                        ricerca_id = ricerca.id,
                        articolo_id = articolo.id,
                        posizione = posizione,

                    ))

            if list_bulk_risultato_ricerca:
                self.db.add_all(list_bulk_storico)
            if list_bulk_storico:
                self.db.add_all(list_bulk_risultato_ricerca)

            await self.db.commit()
            # return final_response
            logger.info(f"JOB COMPLETATO: Salvati {len(list_bulk_storico)} prezzi")
        except Exception as e:
            await self.db.rollback()
            logger.info(f"Errore durante il salvataggio dei dati Amazon: {e}")
            raise   
    

class AmazonApiclient:
    def __init__(self, url: str, apikey: str):
        self.url = url
        self.api_key = apikey

    async def fetch_from_api(self, key_word: str) -> Tuple[list, list]:

        retries = 3
        backoff = 1
        for _ in range(retries):
            try :
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        self.url,
                        params={
                            "domainCode": "it",
                            "keyword": key_word,
                            "page": 1,
                            "sortBy": "price-desc-rank"
                        },
                        headers = {
                            "Cache-control": "no-cache",
                            "axesso-api-key": self.api_key
                        }
                    )

                    response.raise_for_status()
                    data = response.json()

                return data.get("searchProductDetails", []), data.get("foundProducts", [])
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (429, 500, 502, 503):
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise
            except (httpx.ReadTimeout, httpx.ConnectError):
                await asyncio.sleep(backoff)
                backoff *= 2
                continue

        raise RuntimeError("API non disponibile dopo 3 tentativi")

class AmazonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def inserisci_ricerca(self, key_word: str)-> Ricerca:
        ricerca = Ricerca(keyword=key_word.lower())
        self.session.add(ricerca)
        await self.session.flush()

        return ricerca
    
    async def crea_articolo(self, asin_art: str, titolo_art: str) -> Articolo:
        articolo = Articolo(
            asin = asin_art,
            titolo = titolo_art
        )
        self.session.add(articolo)
        await self.session.flush()

        return articolo
    
    
    async def get_articoli_esistenti(self, lista_asins: List[str])-> dict[str, Articolo]:
        result = await self.session.execute(
            select(Articolo).where(Articolo.asin.in_(lista_asins)))
        articoli_dict = {art.asin: art for art in result.scalars().all()}

        return articoli_dict
