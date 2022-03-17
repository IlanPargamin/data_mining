"""
This file scrapes the main page (https://www.freelancer.com/jobs)
INPUTS : None
OUTPUTS: list of dictionaries, where each dictionary corresponds to a job offer and whose keys and associated values
are the main characteristics of the job offer.
"""

import grequests
from bs4 import BeautifulSoup
import pandas as pd
import re
from globals import *
import requests


def get_main():
    """
    Corresponds to the main function of the file.
    Careful: 'main' corresponds to the main page of the website 'freelancer.com/jobs'.
    """
    return scrape_main_page(get_main_html(), title=True, days_left=True, job_desc=False, tags=False, bid=False)


def get_main_html(use_grequest=True):
    """
    Using BeautifulSoup and requests modules, we collect the html "soup" of all the website's relevant urls
    of the main page: www.freelancer.com/jobs.

    We return a list of html soups of the length of our pages range.

    If use_grequest is True, we use grequest. Request otherwise.
    """

    urls = [MAIN_URL + '/jobs/' + f"{str(page)}" for page in range(PAGE_START, PAGE_STOP + 1)]

    if use_grequest:
        rs = (grequests.get(u) for u in urls)
        responses = grequests.map(rs)
        return [BeautifulSoup(response.content, 'html.parser') for response in responses]

    else:
        soups = []
        for page in range(PAGE_START, PAGE_STOP + 1):
            response = requests.get(url=MAIN_URL + '/jobs/' + f"{str(page)}")

            soups.append(BeautifulSoup(response.content, 'html.parser'))

        return soups


def build_dataframe(data_dict):
    """
    Given the dictionary built following the following structure:
                                                                {"page 1": {dictionaries of the lists we scraped},
                                                                {"page 2": {dictionaries of the lists we scraped},
                                                                {"page 3": {dictionaries of the lists we scraped},
                                                                ...}
    we merge the dictionaries of the lists we scraped into one big dataframe.
    We lose the information of which page the data was scraped from.

    :return: a pandas dataframe whose columns are the keys of the {dictionaries of the lists we scraped}.
    """
    df = pd.DataFrame.from_dict(data_dict[f'page {PAGE_START}'])
    for page in list(data_dict.keys())[1:]:
        df = df.append(pd.DataFrame.from_dict(data_dict[page]))
    return df


def scrape_main_page(soups, title=True, days_left=True, job_desc=False, tags=False, bid=False):
    """
    For each parameter, returns a list of scraped data from the main page if parameter True.
    ARGUMENTS: soups, title, days_left, job_desc, tags, bid and url.
    RETURNS a dictionary that follows the following structure:
                                                                {"page 1": {"title":     [job1, job2, ...],
                                                                            "days_left": [job1, job2, ...],
                                                                            "job_desc":  [job1, job2, ...],
                                                                            "tags":      [job1, job2, ...],
                                                                            "bid":       [job1, job2, ...]},
                                                                {"page 2": {...},
                                                                {"page 3": {...},
                                                                ...}
    """

    dict_out = {}
    results_by_page = 50
    page = PAGE_START

    for soup in soups:
        my_page = "page " + str(page)
        dict_out[my_page] = {}
        page += 1

        # job titles
        if title:
            dict_out[my_page]["titles"] = [title.text.strip().split("\n")[0]
                                           for title in
                                           list(soup.find_all('a', class_='JobSearchCard-primary-heading-link'))]

        # time remaining in days to make a bid to a specific job offer
        if days_left:
            dict_out[my_page]["days left to bid"] = [day.string for day in
                                                     list(soup.find_all('span',
                                                                        attrs={
                                                                            'class': 'JobSearchCard-primary-heading'
                                                                                     '-days'}))]

        # job descriptions
        # The following lines of code also creates a list of problematic indexes. That refers to job offers that are not
        # public neither open to bidding.
        problematic_indexes = []
        if job_desc or bid:
            des_all = soup.find_all(class_="JobSearchCard-primary-description")
            desc_list = []
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
        if bid:
            bids_list = []

            for i in range(results_by_page - len(problematic_indexes)):
                if i in problematic_indexes:
                    bids_list.append('')
                    del problematic_indexes[0]  # we delete the problematic index we treated
                    problematic_indexes = [x - 1 for x in problematic_indexes]  # we move the indexes backward
                bids_list.append(list(soup.find_all("div", class_="JobSearchCard-primary-price"))[i].text.strip())
            dict_out[my_page]["bids"] = [x.split("\n")[0] for x in bids_list]

        # links of the job offer: must be scraped
        dict_out[my_page]["url"] = [MAIN_URL + my_url['href'] for my_url in
                                    list(soup.find_all('a', href=True, class_="JobSearchCard-primary-heading-link"))]

    # instead of one dictionary of lists, transform into a list of dictionaries
    data_main = build_dataframe(dict_out)
    return pd.DataFrame(data_main).to_dict(orient="records")


if __name__ == "__main__":
    x = get_main()
    print()
