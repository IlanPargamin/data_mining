import requests
from bs4 import BeautifulSoup

REMOVE_WORD_BUDGET = 6
REMOVE_WORD_SKILLS = 8


def get_project(list_of_projects):
    list_of_dict = list()
    for url in list_of_projects:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        project_dict = get_project_dict(soup)
        project_dict['url'] = url
        list_of_dict.append(project_dict)
    return list_of_dict


def get_verified_traits(soup):
    verified_traits = str(soup.find('ul', class_='verified-list'))
    payment_verified = 'data-tooltip="Payment Verified"'
    made_a_deposit = 'data-tooltip="Made a Deposit"'
    verified_email = 'data-tooltip="Email Verified"'
    verified_traits_list = []
    if verified_email in verified_traits:
        verified_traits_list.append('E-mail Verified')
    if payment_verified in verified_traits:
        verified_traits_list.append('Payment Verified')
    if made_a_deposit in verified_traits:
        verified_traits_list.append('Made a Deposit')
    return verified_traits_list


def get_competition_list(soup):
    names = soup.find_all('a', class_='FreelancerInfo-username')
    rating = soup.find_all('div', class_='Rating Rating--labeled')
    competition_list = []
    for link, rating in zip(names, rating):
        competition_list.append({'url': link.get('href'), 'rating': rating.get('data-star_rating')})
    # remove first worker from list, in freelancer site the first worker doesn't exist.
    competition_list = competition_list[1:]
    return competition_list


def get_project_dict(soup):
    budget = soup.find('p', class_='PageProjectViewLogout-header-byLine').text.strip()[REMOVE_WORD_BUDGET:]
    description = soup.find('p', class_='PageProjectViewLogout-detail-paragraph').text
    skills = soup.find('p', class_='PageProjectViewLogout-detail-tags').text.strip()[REMOVE_WORD_SKILLS:]
    competition_sum = soup.find('h2', class_='Card-heading').text.strip()
    competition_list = get_competition_list(soup)
    verified_traits = get_verified_traits(soup)
    return fill_project_dict(description=description, skills=skills, budget=budget,
                             verified_traits_list=verified_traits, competition_sum=competition_sum,
                             competition_list=competition_list)


def fill_project_dict(description=None, skills=None, project_id=None, budget=None, verified_traits_list=None,
                      competition_sum=None, competition_list=None):
    dict_of_project = {'description': description, 'skills': skills, 'project_id': project_id,
                       'budget': budget, 'verified_traits_list': verified_traits_list,
                       'competition_sum': competition_sum, 'competition_list': competition_list}
    return dict_of_project


if __name__ == '__main__':
    example_url = ['https://www.freelancer.com/projects/website-design/pink-sale-presale?w=f&ngsw-bypass=',
                   'https://www.freelancer.com/projects/logo-design/logo-design-33071777?w=f&ngsw-bypass=']
    # get_project(example_url)
    print(get_project(example_url))
