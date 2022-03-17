import requests
from globals import *
from bs4 import BeautifulSoup

REMOVE_WORD_BUDGET = 6
REMOVE_WORD_SKILLS = 8
REMOVE_DUMMY_EMPLOY = 1


def get_project(list_of_projects):
    """
    This function receives a list of urls and returns a list of dictionaries containing scraped information on every link
    :param list_of_projects:
    :return: list_of_dict
    """
    list_of_dict = list()
    for url in list_of_projects:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        project_dict = get_project_dict(soup)
        project_dict['url'] = url
        list_of_dict.append(project_dict)
    return list_of_dict


def get_verified_traits(soup):
    """
    This function receives a BeautifulSoup element of a specific job and returns a list of traits that are verified
    in account of the job owner
    :param soup:
    :return: verified_traits_list
    """
    verified_traits = str(soup.find('ul', class_='verified-list'))
    payment_verified = 'data-tooltip="Payment Verified"'
    made_a_deposit = 'data-tooltip="Made a Deposit"'
    verified_email = 'data-tooltip="Email Verified"'
    verified_traits_list = [False, False, False]
    if verified_email in verified_traits:
        verified_traits_list[0] = True
    if payment_verified in verified_traits:
        verified_traits_list[1] = True
    if made_a_deposit in verified_traits:
        verified_traits_list[2] = True
    return verified_traits_list


def get_competition_list(soup):
    """
    This function receives a BeautifulSoup element of a specific job offer and returns a list of accounts
    (and their rating) that placed a bid on the received job offer
    :param soup:
    :return: competition_list
    """
    names = soup.find_all('a', class_='FreelancerInfo-username')
    rating = soup.find_all('div', class_='Rating Rating--labeled')

    competition_list = []
    for link, rating in zip(names, rating):
        competition_list.append({'url': MAIN_URL+link.get('href'), 'rating': rating.get('data-star_rating')})

    # remove first worker from list, in freelancer first worker is a dummy.
    competition_list = competition_list[REMOVE_DUMMY_EMPLOY:]

    return competition_list


def get_project_dict(soup):
    """
    This function receives a BeautifulSoup element of a specific job offer and returns a
    dictionary of attributes (via fill_project_dict function) that are
    specific for the job offer (i.e description, budget, etc.).
    :param soup:
    :return: dictionary of job offer attributes
    """
    budget = soup.find('p', class_='PageProjectViewLogout-header-byLine')
    if budget:
        budget = budget.text.strip()[REMOVE_WORD_BUDGET:]

    description = soup.find('p', class_='PageProjectViewLogout-detail-paragraph')
    if description:
        description = description.text

    skills = soup.find('p', class_='PageProjectViewLogout-detail-tags')
    if skills:
        skills = skills.text.strip()[REMOVE_WORD_SKILLS:]

    competition_sum = soup.find('h2', class_='Card-heading')
    if competition_sum:
        competition_sum = competition_sum.text.strip()

    competition_list = get_competition_list(soup)

    verified_traits = get_verified_traits(soup)

    return fill_project_dict(description=description,
                             skills=skills, budget=budget,
                             verified_traits_list=verified_traits,
                             competition_sum=competition_sum,
                             competition_list=competition_list)


def fill_project_dict(description=None,
                      skills=None,
                      budget=None,
                      verified_traits_list=None,
                      competition_sum=None,
                      competition_list=None):
    """
    This function receives parameters, places them in a dictionary and return said dictionary
    :param competition_list, competition_sum, verified_traits_list, budget, project_id, skills, description:
    :return: dictionary of job offer attributes
    """

    dict_of_project = {'description': description, 'skills': skills,
                       'budget': budget, 'verified_traits_list': verified_traits_list,
                       'competition_sum': competition_sum, 'competition_list': competition_list}
    return dict_of_project


if __name__ == '__main__':
    example_url = ['https://www.freelancer.com/projects/website-design/pink-sale-presale?w=f&ngsw-bypass=',
                  'https://www.freelancer.com/projects/logo-design/logo-design-33071777?w=f&ngsw-bypass=']
    get_project(example_url)
    print(get_project(example_url))