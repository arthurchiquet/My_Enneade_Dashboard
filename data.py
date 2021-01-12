import pandas as pd
from PIL import Image
# from server import app, TIMEOUT, cache
from server import app
from google.cloud import storage
from google.oauth2 import service_account
import io
from io import BytesIO
import os
import json


PROJECT_ID = 'vallicorp1'
BUCKET_NAME = "myenneade-data"

def get_credentials(local=False):
    if local:
        credentials_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if '.json' in credentials_raw:
            credentials_raw = open(credentials_raw).read()
        creds_json = json.loads(credentials_raw)
    else:
        creds_json = eval(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    creds_gcp = service_account.Credentials.from_service_account_info(creds_json)
    return creds_gcp

def get_data(chantier, path, filename, json = False, bucket = BUCKET_NAME, project_id = PROJECT_ID, sep=True):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f'{chantier}/{path}/{filename}')
    data = blob.download_as_string()
    if sep:
        if json:
            return pd.read_json(io.BytesIO(data), sep=';', compression='bz2')
        else:
            return pd.read_csv(io.BytesIO(data), encoding = 'utf-8', sep=';', memory_map = True)
    else:
        if json:
            return pd.read_json(io.BytesIO(data), compression='bz2')
        else:
            return pd.read_csv(io.BytesIO(data), encoding = 'utf-8', memory_map = True)

def download_image(chantier, filename, bucket = BUCKET_NAME, project_id = PROJECT_ID, rm = True):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=PROJECT_ID)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f'{chantier}/{filename}')
    blob.download_to_filename('plan.jpeg')
    img = Image.open("plan.jpeg")
    if rm:
        os.remove('plan.jpeg')
    return img

def export_data(df, chantier, path, filename, bucket = BUCKET_NAME, project_id = PROJECT_ID):
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f'{chantier}/{path}/{filename}')
    blob.upload_from_string(df.to_csv(index=False))

