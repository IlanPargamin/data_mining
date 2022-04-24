import requests
import pymysql
from globals import *
import pandas as pd


def get_ratio_to_usd(original_currency):
    """
    given a three-letter code for a currency, call the api to get the ratio to USD
    """
    api_key = 'b4acb2db3f994383cac50d9a'
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{original_currency}'

    # Get current ratio to sent currency 3-letters format
    response = requests.get(url)
    data = response.json()
    ratio = data['conversion_rates']['USD']
    return ratio


def enrich_budget_currency():
    """
    Convert foreign currencies values in the table Budget
    """
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE freelancer")

    query = '''
    select *
    from Budget
    '''

    budget_table = pd.read_sql(query, connection)

    for index, row in budget_table.iterrows():
        currency_original = row['currency_original']
        if currency_original == 'USD':
            cursor.execute(f"""
                        UPDATE Budget SET currency = 'USD' WHERE id = {row['id']};""")
        if currency_original != 'USD' and row['currency'] != 'USD':
            conversion_ratio = get_ratio_to_usd(currency_original) if currency_original else None

            min_usd = round(int(row["min_usd"]) * conversion_ratio, 1) if str(row["min_usd"]) != 'nan' else 'Null'
            max_usd = round(int(row["max_usd"]) * conversion_ratio, 1) if str(row["max_usd"]) != 'nan' else 'Null'

            cursor.execute(f"""
            UPDATE Budget SET min_usd = {min_usd} WHERE id = {row['id']};""")
            cursor.execute(f"""
            UPDATE Budget SET max_usd = {max_usd} WHERE id = {row['id']};""")
            cursor.execute(f"""
            UPDATE Budget SET currency = 'USD' WHERE id = {row['id']};""")

    connection.commit()
