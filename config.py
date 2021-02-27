from sqlalchemy import create_engine
import os
import requests


#### CREATION D'UN URL DE CONNEXION A LA BASE DE DONNNEES SQL
#### 'DATABASE_URL' EST DÉFINI COMME VARAIABLE D'ENVIRONNEMENT POUR DAVANTAGE DE SECURITÉ
#### SOUS LA FORME 'postrgesql://username:password@host:port/database'

engine = create_engine(os.environ["DATABASE_URL"])
