#### VOIR chantier_mgmt.py pour plus de détails

from sqlalchemy import Table
from flask_sqlalchemy import SQLAlchemy
from config import engine

db = SQLAlchemy()


class Capteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_capteur = db.Column(db.String(15))
    nom_chantier = db.Column(db.String(50))
    type = db.Column(db.String(15))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)


class Secteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_secteur = db.Column(db.String(15))
    nom_chantier = db.Column(db.String(50))
    lat1 = db.Column(db.Float)
    lat2 = db.Column(db.Float)
    lon1 = db.Column(db.Float)
    lon2 = db.Column(db.Float)


Capteur_tbl = Table("capteur", Capteur.metadata)
Secteur_tbl = Table("secteur", Secteur.metadata)


def create_table():
    Capteur.metadata.create_all(engine)


def ajout_capteur(nom_capteur, nom_chantier, type, lat, lon):
    ins = Capteur_tbl.insert().values(
        nom_capteur=nom_capteur,
        nom_chantier=nom_chantier,
        type=type,
        lat=lat,
        lon=lon,
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()


def ajout_secteur(nom_secteur, nom_chantier, lat1, lat2, lon1, lon2):
    ins = Secteur_tbl.insert().values(
        nom_secteur=nom_secteur,
        nom_chantier=nom_chantier,
        lat1=lat1,
        lat2=lat2,
        lon1=lon1,
        lon2=lon2,
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()


def maj_capteur(nom_capteur, nom_chantier, type, lat, lon):
    update = (
        Capteur_tbl.update()
        .values(lat=lat, lon=lon)
        .where(
            (Capteur_tbl.c.nom_capteur == nom_capteur)
            & (Capteur_tbl.c.nom_chantier == nom_chantier)
        )
    )

    conn = engine.connect()
    conn.execute(update)
    conn.close()


def maj_secteur(nom_secteur, nom_chantier, lat1, lat2, lon1, lon2):
    update = (
        Secteur_tbl.update()
        .values(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
        .where(
            (Secteur_tbl.c.nom_secteur == nom_secteur)
            & (Secteur_tbl.c.nom_chantier == nom_chantier)
        )
    )

    conn = engine.connect()
    conn.execute(update)
    conn.close()


def supp_capteur(nom_capteur, nom_chantier):
    delete = Capteur_tbl.delete().where(
        (Capteur_tbl.c.nom_capteur == nom_capteur)
        & (Capteur_tbl.c.nom_chantier == nom_chantier)
    )
    conn = engine.connect()
    conn.execute(delete)
    conn.close()


def supp_secteur(nom_secteur, nom_chantier):
    delete = Secteur_tbl.delete().where(
        (Secteur_tbl.c.nom_secteur == nom_secteur)
        & (Secteur_tbl.c.nom_chantier == nom_chantier)
    )
    conn = engine.connect()
    conn.execute(delete)
    conn.close()
