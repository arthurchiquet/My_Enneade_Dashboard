from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from config import engine
import pandas as pd

db = SQLAlchemy()


class Chantier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_chantier = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    adresse = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    zoom=db.Column(db.Float)
    x1 = db.Column(db.Float)
    x2 = db.Column(db.Float)
    y1 = db.Column(db.Float)
    y2 = db.Column(db.Float)


Chantier_tbl = Table("chantier", Chantier.metadata)


def create_table():
    Chantier.metadata.create_all(engine)


def add_chantier(nom_chantier, username, adresse, lat, lon, zoom=15, x1=0, x2=0, y1=0, y2=0):
    ins = Chantier_tbl.insert().values(
        nom_chantier=nom_chantier,
        username=username,
        adresse=adresse,
        lat=lat,
        lon=lon,
        zoom=zoom,
        x1=x1,
        x2=x2,
        y1=y1,
        y2=y2
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()

def del_chantier(nom_chantier):
    delete = Chantier_tbl.delete().where(Chantier_tbl.c.nom_chantier == nom_chantier)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()

def update_chantier(nom_chantier, x1, x2, y1, y2):
    update = (
        Chantier_tbl.update().values(x1=x1).where(Chantier_tbl.c.nom_chantier == nom_chantier),
        Chantier_tbl.update().values(x2=x2).where(Chantier_tbl.c.nom_chantier == nom_chantier),
        Chantier_tbl.update().values(y1=y1).where(Chantier_tbl.c.nom_chantier == nom_chantier),
        Chantier_tbl.update().values(y2=y2).where(Chantier_tbl.c.nom_chantier == nom_chantier)

    )

    conn = engine.connect()
    conn.execute(update)
    conn.close()


def afficher_chantier():
    select_stmt = select(
        [
            Chantier_tbl.c.nom_chantier,
            Chantier_tbl.c.username,
            Chantier_tbl.c.adresse,
        ]
    )

    conn = engine.connect()
    results = conn.execute(select_stmt)

    chantiers = []

    for result in results:
        chantiers.append(
            {
                "nom_chantier": result[0],
                "username": result[1],
                "adresse": result[2],
            }
        )

    conn.close()

    return chantiers
