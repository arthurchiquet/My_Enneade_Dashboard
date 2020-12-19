from sqlalchemy import Table
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from config import engine
import pandas as pd

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    profil = db.Column(db.Integer)

User_tbl = Table("user", User.metadata)

def create_table():
    User.metadata.create_all(engine)

def update_output():
    con = engine.connect()
    list_users = pd.read_sql("user", con=con).username.tolist()
    con.close()
    return [{"label": user, "value": user} for user in list_users]

def add_user(username, password, email, profil):
    hashed_password = generate_password_hash(password, method="sha256")

    ins = User_tbl.insert().values(
        username=username,
        email=email,
        password=hashed_password,
        profil=profil,
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()


def update_password(username, password):
    hashed_password = generate_password_hash(password, method="sha256")



    update = (
        User_tbl.update()
        .values(password=hashed_password)
        .where(User_tbl.c.username == username)
    )

    conn = engine.connect()
    conn.execute(update)
    conn.close()

def update_profil(username, profil):
    update = (
        User_tbl.update().values(profil=profil).where(User_tbl.c.username == username)
    )

    conn = engine.connect()
    conn.execute(update)
    conn.close()


def del_user(username):
    delete = User_tbl.delete().where(User_tbl.c.username == username)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()


def show_users():
    select_stmt = select(
        [User_tbl.c.id, User_tbl.c.username, User_tbl.c.email, User_tbl.c.profil]
    )

    conn = engine.connect()
    results = conn.execute(select_stmt)

    users = []

    for result in results:
        users.append(
            {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "profil": str(result[3]),
            }
        )

    conn.close()

    return users
