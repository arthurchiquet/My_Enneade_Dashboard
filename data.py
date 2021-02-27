#### Import des modules google cloud

from google.cloud import storage
from google.oauth2 import service_account

#### Import des modules python

import pandas as pd
from PIL import Image
from io import BytesIO
import io
import os
import json

from server import app, TIMEOUT, cache

#### PROJECT_ID : nom du projet crée dans GOOGLE CLOUD PLATEFORM
#### BUCKET_ID : nom de la bucket de stockage de données crée dans GOOGLE CLOUD STORAGE
PROJECT_ID = "vallicorp1"
BUCKET_NAME = "myenneade-data"

#### FONCTION PERMETTANT DE RÉCUPÉRER LES CREDENTIALS STOCKÉS DANS LA VARIABLE D'ENVIRONNEMENT
#### GOOGLE_APPLICATION_CREDENTIALS NÉCESSAIRE À LA CONNEXION GOOGLE STORAGE
def get_credentials(local=True):
    if local:
        credentials_raw = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if ".json" in credentials_raw:
            credentials_raw = open(credentials_raw).read()
        creds_json = json.loads(credentials_raw)
    else:
        creds_json = eval(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    creds_gcp = service_account.Credentials.from_service_account_info(creds_json)
    return creds_gcp


#### LE DECORATEUR @cache.memoize() PERMET DE STOCKER LA VALEUR DE LA FONCTION DEFINIT CI-DESSOUS
#### PERMET UN UNIQUE CHARGEMENT ET CALCUL DES DONNÉES ET RESTITUE DIRECTEMENT LA VALEUR
#### PAR LA SUITE LORSQUE LA FONCTION EST APPELÉÉ

@cache.memoize(timeout=TIMEOUT)
def query_data(
    chantier, path, types, filename, bucket=BUCKET_NAME, project_id=PROJECT_ID, sep=True
):
    '''fonction permettant le telechargement des données stockées dans la bucket google storage
    sous forme de CSV et les retourne sous forme d'un Dataframe'''

    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"{chantier}/{path}/{types}/{filename}")
    data = blob.download_as_string()
    if sep:
        return pd.read_csv(io.BytesIO(data), encoding="utf-8", sep=";", memory_map=True)
    else:
        return pd.read_csv(io.BytesIO(data), encoding="utf-8", memory_map=True)


def get_data(
    chantier, path, types, filename, bucket=BUCKET_NAME, project_id=PROJECT_ID, sep=True
):
    '''fonction permettant le telechargement des données stockées dans la bucket google storage
    sous forme de CSV et les retourne sous forme d'un Dataframe'''

    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"{chantier}/{path}/{types}/{filename}")
    data = blob.download_as_string()
    if sep:
        return pd.read_csv(io.BytesIO(data), encoding="utf-8", sep=";", memory_map=True)
    else:
        return pd.read_csv(io.BytesIO(data), encoding="utf-8", memory_map=True)

#### fonction permettant de beneficier de la focntion de mise en cache
def memoized_data(chantier, path, types, filename):
    return query_data(chantier, path, types, filename)


#### FONCTION PERMETTANT DE TELECHARGER UNE IMAGE STOCKÉE DANS UNE BUCKET GOOGLE STORAGE
def download_image(
    chantier, filename, bucket=BUCKET_NAME, project_id=PROJECT_ID, rm=True
):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=PROJECT_ID)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"{chantier}/{filename}")
    blob.download_to_filename("plan.jpeg")
    img = Image.open("plan.jpeg")
    if rm:
        os.remove("plan.jpeg")
    return img

#### FONCTION PERMETTANT DE RETOURNER LA LISTE DES FICHIERS PRÉSENTS DANS UN SOUS-SOSSIER GOOGLE STORAGE
def list_files(prefix, bucketname=BUCKET_NAME, projetcid=PROJECT_ID):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=projetcid)
    bucket = client.get_bucket(bucketname)
    files = bucket.list_blobs(prefix=prefix)
    fileList = [file.name for file in files if "." in file.name]
    docs = [i.replace(prefix, "")[:-4] for i in fileList]
    return docs

#### FONCTION PERMETTANT D'EXPORTER SOUS FORME DE CSV DANS UN DOSSIER GOOGLE STORAGE
def export_data(
    df, chantier, path, types, filename, bucket=BUCKET_NAME, project_id=PROJECT_ID
):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f"{chantier}/{path}/{types}/{filename}")
    blob.upload_from_string(df.to_csv(index=False, sep=";"))
