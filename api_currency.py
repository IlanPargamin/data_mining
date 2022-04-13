api_key = 'b4acb2db3f994383cac50d9a'


def get_ratio_to_usd(original_currency):
    import requests

    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{original_currency}'

    # Get current ratio to sent currency 3-letters format
    response = requests.get(url)
    data = response.json()
    ratio = data['conversion_rates']['USD']
    return ratio
