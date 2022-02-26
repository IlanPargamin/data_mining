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
        response = requests.get(url=MAIN_URL + '/jobs/' + f"{str(page)}" + "/" + f'?results={RESULTS_BY_PAGE}')
    return BeautifulSoup(response.content, 'html.parser')


def scrape_job_page(soup, titles=True, days_left=True, job_desc=True, tags=True, bids=True, links=True):
    """
    For each parameter, returns a list of scraped data if parameter True
    :param soup
    :param titles
    :param days_left
    :param job_desc
    :param tags
    :param bids
    :param links
    :return: out: a dictionary where each True parameter is a key and the associated value is the list of scraped data
    """
    out = {}

    # job titles
    if titles:
        out["titles"] = [x.text.strip().split("\n")[0]
                         for x in list(soup.find_all('a', class_='JobSearchCard-primary-heading-link'))]

    # time remaining in days to make a bid to a specific job offer
    if days_left:
        out["days left to bid"] = [x.string for x in
                            list(soup.find_all('span', attrs={'class': 'JobSearchCard-primary-heading-days'}))]

    # job descriptions
    # The following lines of code also creates a list of problematic indexes. That refers to job offers that are not
    # public neither open to bidding.
    if job_desc or bids:
        des_all = soup.find_all(class_="JobSearchCard-primary-description")
        desc_list = []
        problematic_indexes = []
        for i in range(RESULTS_BY_PAGE):
            desc_list.append(des_all[i].text.strip())
            if 'Please Sign Up or Login to see details.' in des_all[i].text.strip():
                problematic_indexes.append(i)
        if job_desc:
            out["Job description"] = desc_list

    # job tags corresponding to the job offer
    if tags:
        out["tags"] = list(map((lambda s: re.sub(r'\n', ', ', s)), [tag.text.strip()
                                                                    for tag in list(
                soup.find_all("div", class_="JobSearchCard-primary-tags"))]))

    # average bids
    # There is no bid if the index is problematic. We append the list with ''
    if bids:
        bids_list = []
        for i in range(RESULTS_BY_PAGE - len(problematic_indexes)):
            if i in problematic_indexes:
                bids_list.append('')
                del problematic_indexes[0]  # we delete the problematic index we treated
                problematic_indexes = [x - 1 for x in problematic_indexes]  # we move the indexes backward
            bids_list.append(list(soup.find_all("div", class_="JobSearchCard-primary-price"))[i].text.strip())
        out["bids"] = [x.split("\n")[0] for x in bids_list]

    # links of the job offer
    if links:
        out["links"] = [MAIN_URL + x['href'] for x in
                        list(soup.find_all('a', href=True, class_="JobSearchCard-primary-heading-link"))]

    return out


def build_dataframe(data_dict):
    """
    Given the dictionary of lists we scraped,
    we build a pandas dataframe where each list is a column.
    :return: a pandas dataframe
    """
    return pd.DataFrame.from_dict(data_dict)


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

    for page in range(PAGE_START, PAGE_STOP):
        soup = get_soup(page)
        scraped_data = scrape_job_page(soup, titles=True,
                                       days_left=True,
                                       job_desc=False,
                                       tags=True,
                                       bids=True,
                                       links=True)

        df = build_dataframe(scraped_data)
        print(df)

        # TODO mine deeper:
        #     *rating of the employer
        #     *location of the employer
        #     *other job offers from this employer
        #     *similar jobs
        #     *list of bidders:
        #         - name
        #         - description
        #         - review
        #         - link to profile

        # TODO merge with Shai's code

        # TODO write readme.md

        # TODO get requirements file

        # TODO write tests


if __name__ == "__main__":
    main()
