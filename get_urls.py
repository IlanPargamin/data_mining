"""
INPUT : a list of dictionaries which all possesses the key "url"
OUTPUT: the list of all the values of the key "url" from all dictionaries.

"""


def get_urls(list_of_dicts):
    """
    corresponds to the main function.
    """
    urls = []
    for i in range(len(list_of_dicts)):
        urls.append(list_of_dicts[i]['url'])
    return urls


if __name__ == "__main__":
    list_main_dicts = [{'url': 'https://www.freelancer.com/project'}]
    x=get_urls(list_main_dicts)
    print()
