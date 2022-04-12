import requests
import json
import numpy as np
import pandas as pd
from pandas import json_normalize

my_client_id = "mx9ummf6t4l5ck4i"
my_client_secret = "DLstFXms"
my_scope = "emsi_open"


def create_access_token(client_id, client_secret, scope):
    """
    Given client_id, client_secret and scope, establishes a connection with the api and returns access_token as a string
    """
    auth_endpoint = "https://auth.emsicloud.com/connect/token"
    payload_main = "client_id=" + client_id \
                   + "&client_secret=" + client_secret \
                   + "&grant_type=client_credentials&scope=" + scope
    headers_main = {'content-type': 'application/x-www-form-urlencoded'}
    return json.loads((requests.request("POST", auth_endpoint, data=payload_main, headers=headers_main)).text)[
        'access_token']


def get_skill_emsi(skill, confidence_interval, access_token):
    """
    given a skill (string type), finds correspondences in the emsi database and returns them in a pandas dataframe
    """
    skills_from_db_endpoint = "https://emsiservices.com/skills/versions/latest/extract"
    payload = "{ \"text\": \"... " + skill + " ...\", \"confidenceThreshold\": " + confidence_interval + " }"

    headers = {
        'authorization': "Bearer " + access_token,
        'content-type': "application/json"
    }

    response = requests.request("POST", skills_from_db_endpoint, data=payload.encode('utf-8'), headers=headers)

    return pd.DataFrame(json_normalize(response.json()['data']))


