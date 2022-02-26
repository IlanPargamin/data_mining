import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

MAIN_URL = 'https://www.freelancer.com'
RESULTS_BY_PAGE = 50
PAGE_START = 1
PAGE_STOP = 20


def get_soup(page):
    """
    Using the modules request and BeautifulSoup, we download the HTML code of the website.
    User must input the constants of his choice at the beginning of the file.
    :param page: the page number of the website. Allows us to loop over pages.
    :return: soup, the HTML code in the BeautifulSoup format.
    """
    if page == 1:
        response = requests.get(url=MAIN_URL + '/jobs' + f'?results={RESULTS_BY_PAGE}')
    else:
        # time.sleep(1)
        response = requests.get(url=MAIN_URL + '/jobs' + f"{str(page)}" + "/" + f'?results={RESULTS_BY_PAGE}')
    return BeautifulSoup(response.content, 'html.parser')


def get_titles(soup):
    """
    Given the html code of the website, get_titles returns a list of all the job titles in the specified page of the
    website.
    :param soup
    :return: a list of all job titles
    """

    title_all_html = soup.find_all('a', class_='JobSearchCard-primary-heading-link')
    titles = []
    for title in title_all_html:
        titles.append(title.text.strip())
    return [x.split("\n")[0] for x in titles]


def get_days_left(soup):
    """
    returns a list whose elements are the time remaining in days to make a bid to a specific job offer.
    Ex: "6 days left"
    :param soup
    """
    days_all = soup.find_all('span', attrs={'class': 'JobSearchCard-primary-heading-days'})
    days_left = []
    for day in days_all:
        days_left.append(day.string)
    return days_left


def get_job_desc(soup):
    """
    returns a list with all the job descriptions.

    The function also creates a list of problematic indexes : job descriptions indicating "Please Sign Up or Login to
    see details".
    It is an indication that the job offer is not public and there is no visible public bid to scrape. We use the list
    problematic indexes in the get_bid function.

    :param soup
    :return: the list of the job descriptions, the list of problematic indexes
    """
    des_all = soup.find_all(class_="JobSearchCard-primary-description")
    desc = []
    problematic_indexes = []
    for i in range(RESULTS_BY_PAGE):
        desc.append(des_all[i].text.strip())

        if 'Please Sign Up or Login to see details.' in des_all[i].text.strip():
            problematic_indexes.append(i)
    return desc, problematic_indexes


def get_job_tags(soup):
    """
    Returns a list with all the job tags that correspond to the job offers.
    Ex: if this is a data science job offer, the tags could be "data science, data mining, python"
    :param soup
    :return:
    """
    tags_all = soup.find_all("div", class_="JobSearchCard-primary-tags")
    tags = []
    for tag in tags_all:
        tags.append(tag.text.strip())
    return list(map((lambda s: re.sub(r'\n', ', ', s)), tags))


def get_bids(soup, prob_indexes):
    """
    Returns a list with all the average bids associated with the job offers.
    The format depends on the job offer: sometimes it will be a range ('500-1000 USD'), a price per hours ('5 USD per
    hour') or a fixed price ('5000 USD'). The currency is always USD.
    As described in the docstring of get_desc, some job offers do not provide a visible average bid. When we reach
    these problematic indexes, we insert an empty average bid.
    :param soup
    :param prob_indexes: the indexes for which there is no average bid to scrape
    :return: a list of all the average bids in different formats
    """
    bid_all = soup.find_all("div", class_="JobSearchCard-primary-price")
    bids = []
    for i in range(RESULTS_BY_PAGE - len(prob_indexes)):
        if i in prob_indexes:
            bids.append('')
            del prob_indexes[0]  # we delete the problematic index we treated
            prob_indexes = [x - 1 for x in prob_indexes]  # we move the indexes backward
        bids.append(bid_all[i].text.strip())
    return [x.split("\n")[0] for x in bids]


def get_links(soup):
    """
    Returns a list of the links of all the job offers.
    :param soup
    :return:
    """
    return [MAIN_URL + x['href'] for x in list(soup.find_all('a', href=True, class_="JobSearchCard-primary-heading-link"))]



def build_dataframe(titles, days_left, desc, tags, bids):
    """
    Given the lists we built using the functions get_titles, get_days_left, get_job_desc, get_job_tags and get_bids,
    we build a pandas dataframe where each list is a column.
    :param titles: list of the job titles
    :param days_left: list of the days left to make a bid
    :param desc: list of the job descriptions
    :param tags: list of the job tags
    :param bids: list of the amounts of the average bids of the job offers
    :return: a pandas dataframe
    """
    return pd.DataFrame({
        "titles": titles,
        "days_left": days_left,
        "desc": desc,
        "tags": tags,
        "bids": bids
    })


def printing_options(print_opt=None):
    """
    Sets options for printing the full pandas dataframe.
    :return:
    """
    if print_opt == 'full':
        pd.set_option("display.max_rows", None, "display.max_columns", None)





def main():
    """
    Our main function.
    Loops over the page range characterized by the constants at the beginning of the document.
    For each page, the function builds a pandas dataframe with the data collected from the website
    'https://www.freelancer.com/jobs/'.
    It prints the dataframes without saving it.
    :return: no return
    """
    if PAGE_START > PAGE_STOP:
        raise ValueError(f'You cannot start at the page {PAGE_START} and finish at page {PAGE_STOP}. '
                         f'PAGE_START must be inferior or equal to PAGE_STOP.')

    printing_options(print_opt='full')

    for page in range(PAGE_START, PAGE_STOP):
        soup = get_soup(page)
        links = get_links(soup)
        titles = get_titles(soup)
        days_left = get_days_left(soup)
        job_desc, problematic_indexes = get_job_desc(soup)
        job_tags = get_job_tags(soup)
        bids = get_bids(soup, problematic_indexes)
        df = build_dataframe(titles, days_left, job_desc, job_tags,
                             bids)
        print(df)
        # TODO mine deeper
        # TODO merge with Shai's code
        # TODO write readme.md
        # TODO get requirements file


if __name__ == "__main__":
    main()
