import requests
import json
import numpy as np
import pandas as pd
from pandas import json_normalize
import pathlib
import os
import pymysql
from globals import *

my_client_id = "u2e1c3ba8oh9v16r"
my_client_secret = "Kd3uFDeG"
my_scope = "emsi_open"


def get_catalogues():
    """
    extracts skill_catalogue from the file catalogues.json
    """
    # path = str(pathlib.Path(__file__).parent.resolve())
    path = '/Users/ilanpargamin/Desktop/ITC/core/data_mining_project'
    with open(path + "/catalogues.json", "r") as read_file:
        catalogues_att = json.load(read_file)

    return catalogues_att['skill_catalogue']


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


def levenshtein(seq1, seq2):
    """
    Returns levenshtein distance between two words
    """
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1
                )
            else:
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x, y - 1] + 1
                )
    return matrix[size_x - 1, size_y - 1]


def get_info():
    """
    Loads the skills from our json file catalogues.json, returns the descriptions and the names of the associated skills
    from the emsi database
    """
    access_token = create_access_token(my_client_id, my_client_secret, my_scope)
    skill_catalogue = get_catalogues()
    confidence_interval = '0.6'

    # turn skill_catalogue into one long string
    skills = ', '.join(skill_catalogue)

    # send query and get response in pandas df
    return get_skill_emsi(skills, confidence_interval, access_token)


def skills_corr():
    """
    Given a list of skills and a pandas dataframe of skills, establishes correspondence between skills.
    Returns a dictionary.
    """
    skill_catalogue = get_catalogues()
    skills_df = get_info()
    # ATTENTION : ne pas update ce qui existe déjà

    # big_no = ['Programming', 'Trading', '']
    corr_dict = {}
    for skill_sql in skill_catalogue:
        for skill_emsi in skills_df['skill.name'].tolist():
            if (levenshtein(skill_sql, skill_emsi) < 2 or skill_sql in skill_emsi):  # and (skill_sql not in big_no):
                # add related skills? in another table
                # add description to table Skill in SQL
                name = skills_df[skills_df['skill.name'] == skill_emsi]['skill.name'].tolist()[0]
                des = skills_df[skills_df['skill.name'] == skill_emsi]['skill.description'].tolist()[0]
                corr_dict[skill_sql] = [name, des]
    return corr_dict


def skill_descriptions_to_sql():
    """
    Given the correspondence dictionary between skills, insert the description of skills into the sql database
    """
    corr_dict = skills_corr()

    # clean descriptions (remove "")
    for skill_sql in corr_dict:
        skill_info = corr_dict[skill_sql]
        if skill_info[1]:
            skill_info[1] = skill_info[1].replace('\"', "")
            skill_info[1] = skill_info[1].replace('\'', "")
            skill_info[0] = skill_info[1].replace('\'', "")

    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE freelancer")

    # # create column
    # cursor.execute("""
    # ALTER TABLE Skill
    # ADD COLUMN description VARCHAR(10000) AFTER name;
    # """)

    for skill_sql in corr_dict:
        skill_info = corr_dict[skill_sql]
        # long_name = skill_info[0]
        description = skill_info[1]
        cursor.execute(f"""
        UPDATE Skill SET description = \'{description}\' WHERE name = \'{skill_sql}\';""")
    connection.commit()
