import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

PAGE_START = 1
PAGE_STOP = 3
MAIN_URL = 'https://www.freelancer.com'


def get_main_html():
    """
    Using BeautifulSoup and requests modules, we collect the html "soup" of all the website's relevant urls
    of the main page: www.freelancer.com/jobs.
    We return a list of html soups of the length of our pages range.
    """

    if PAGE_START > PAGE_STOP:
        raise ValueError(f'You cannot start at the page {PAGE_START} and finish at page {PAGE_STOP}. '
                         f'PAGE_START must be inferior or equal to PAGE_STOP.')

    soups = []
    for page in range(PAGE_START, PAGE_STOP + 1):

        if page == 1:
            response = requests.get(url=MAIN_URL + '/jobs')
        else:
            # time.sleep(1)
            response = requests.get(url=MAIN_URL + '/jobs/' + f"{str(page)}")

        soups.append(BeautifulSoup(response.content, 'html.parser'))

    return soups


def scrape_main_page(soups, titles=True,
                     days_left=True,
                     job_desc=True,
                     tags=True,
                     bids=True,
                     links=True):
    """
    For each parameter, returns a list of scraped data from the main page if parameter True
    :param soups
    :param titles
    :param days_left
    :param job_desc
    :param tags
    :param bids
    :param links
    :return: dict_out: a dictionary where each True parameter is a key and the associated value is the list of scraped
    data
    """

    dict_out = {}
    results_by_page = 50
    page = PAGE_START

    for soup in soups:
        my_page = "page " + str(page)
        dict_out[my_page] = {}
        page += 1

        # job titles
        if titles:
            dict_out[my_page]["titles"] = [x.text.strip().split("\n")[0]
                                           for x in
                                           list(soup.find_all('a', class_='JobSearchCard-primary-heading-link'))]

        # time remaining in days to make a bid to a specific job offer
        if days_left:
            dict_out[my_page]["days left to bid"] = [x.string for x in
                                                     list(soup.find_all('span',
                                                                        attrs={
                                                                            'class': 'JobSearchCard-primary-heading'
                                                                                     '-days'}))]

        # job descriptions
        # The following lines of code also creates a list of problematic indexes. That refers to job offers that are not
        # public neither open to bidding.
        if job_desc or bids:
            des_all = soup.find_all(class_="JobSearchCard-primary-description")
            desc_list = []
            problematic_indexes = []
            for i in range(len(des_all)):
                desc_list.append(des_all[i].text.strip())
                if 'Please Sign Up or Login to see details.' in des_all[i].text.strip():
                    problematic_indexes.append(i)
            if job_desc:
                dict_out[my_page]["Job description"] = desc_list

        # job tags corresponding to the job offer
        if tags:
            dict_out[my_page]["tags"] = list(map((lambda s: re.sub(r'\n', ', ', s)), [tag.text.strip()
                                                                                      for tag in list(
                    soup.find_all("div", class_="JobSearchCard-primary-tags"))]))

        # average bids
        # There is no bid if the index is problematic. We append the list with ''
        if bids:
            bids_list = []
            for i in range(results_by_page - len(problematic_indexes)):
                if i in problematic_indexes:
                    bids_list.append('')
                    del problematic_indexes[0]  # we delete the problematic index we treated
                    problematic_indexes = [x - 1 for x in problematic_indexes]  # we move the indexes backward
                bids_list.append(list(soup.find_all("div", class_="JobSearchCard-primary-price"))[i].text.strip())
            dict_out[my_page]["bids"] = [x.split("\n")[0] for x in bids_list]

        # links of the job offer
        if links:
            dict_out[my_page]["links"] = [MAIN_URL + x['href'] for x in
                                          list(
                                              soup.find_all('a', href=True,
                                                            class_="JobSearchCard-primary-heading-link"))]

    return dict_out


def build_dataframe(data_dict):
    """
    Given the dictionary "page #": dictionaries of the lists we scraped,
    we build several pandas dataframes, each one corresponding to a page, where each list is a column, and we merge
    them in one big dataframe.
    :return: a pandas dataframe
    """
    df = pd.DataFrame.from_dict(data_dict[f'page {PAGE_START}'])
    for page in list(data_dict.keys())[1:]:
        df = df.append(pd.DataFrame.from_dict(data_dict[page]))
    return df


def get_column_as_list(dataframe, column):
    """
    given a dataframe and the name of a column, extracts the values of the column into
    a list.
    """
    return dataframe[column].tolist()


def join_scrapes(data_main, data_project):
    """
    join data_main and data_project into one pandas dataframe
    The common unique key for merging is the links
    """
    pass


if __name__ == "__main__":
    soups_main = get_main_html()
    dict_main = scrape_main_page(soups_main, titles=True,
                                 days_left=True,
                                 job_desc=True,
                                 tags=True,
                                 bids=True,
                                 links=True)
    data_main = build_dataframe(dict_main)

    urls_project = get_column_as_list(data_main, column="links")
    print()

