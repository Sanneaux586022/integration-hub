from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Articolo(Base):
    __tablename__= "articoli"
    id = Column(Integer, primary_key=True)
    asin = Column(String(20), unique=True, index=True, nullable=False)
    titolo = Column(String(500))

    prezzi = relationship("StoricoPrezzo", back_populates="articolo", cascade="all, delete")


class StoricoPrezzo(Base):
    __tablename__ = "storico_prezzi"

    id = Column(Integer, primary_key=True)
    articolo_id = Column(
        Integer,
        ForeignKey("articoli.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    prezzo = Column(Numeric(10,2), nullable=False)
    data_rilevazione = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    articolo = relationship("Articolo", back_populates="prezzi")

class Ricerca(Base):
    __tablename__ = "ricerche"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255),nullable=False, index=True)
    data_ricerca = Column(DateTime(timezone=True), server_default=func.now())

    # relazione 1 --> N
    risultati = relationship("RisultatoRicerca", back_populates="ricerca", cascade="all, delete")



class RisultatoRicerca(Base):
    __tablename__= "risultati_ricerca"


    id = Column(Integer, primary_key=True, index=True)
    ricerca_id = Column(
        Integer, 
        ForeignKey("ricerche.id", ondelete="CASCADE") ,
        nullable=False
    )
    articolo_id = Column(
        Integer,
        ForeignKey("articoli.id", ondelete="CASCADE"),
        nullable=False
    )
    posizione = Column(Integer)

    # relazione N --> 1
    ricerca = relationship("Ricerca", back_populates="risultati")
    articolo = relationship("Articolo")

    __table_args__ = (
        UniqueConstraint("ricerca_id", "articolo_id", name="uix_ricerca_asin"),
    )