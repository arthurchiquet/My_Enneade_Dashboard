from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from config import engine
import pandas as pd

db = SQLAlchemy()

class Chantier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_chantier = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    adresse = db.Column(db.String(50), unique=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

Chantier_tbl = Table("chantier", Chantier.metadata)

def create_table():
    Chantier.metadata.create_all(engine)

def update_output():
    con = engine.connect()
    list_chantier = pd.read_sql("chantier", con=con).nom_chantier.tolist()
    con.close()
    return [{"label": chantier, "value": chantier} for chantier in list_chantier]

def add_chantier(nom_chantier, username, adresse, lat, lon):
    ins = Chantier_tbl.insert().values(
        nom_chantier=nom_chantier,
        username=username,
        adresse=adresse,
        lat=lat,
        lon=lon,
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()

def del_chantier(nom_chantier):
    delete = Chantier_tbl.delete().where(Chantier_tbl.c.nom_chantier == nom_chantier)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()


def afficher_chantier():
    select_stmt = select(
        [Chantier_tbl.c.nom_chantier, Chantier_tbl.c.username, Chantier_tbl.c.adresse, Chantier_tbl.c.lat, Chantier_tbl.c.lon]
    )

    conn = engine.connect()
    results = conn.execute(select_stmt)

    chantiers = []

    for result in results:
        chantiers.append(
            {
                "id": result[0],
                "nom_chantier": result[1],
                "username": result[2],
                "adresse": result[3],
            }
        )

    conn.close()

    return chantiers
