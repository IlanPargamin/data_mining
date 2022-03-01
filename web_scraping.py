"""
main file
To choose the range of the pages to scrape, you can modify the global variables in the file globals.py
"""

from get_project import get_project
from get_main import get_main
from get_urls import get_urls


def join_lists_of_dicts(dict_list1, dict_list2):
    """
    given two lists of dictionaries, merges dictionaries together 1 by 1
    dict_list1 = [dict_a, dict_b]
    dict_list2 = [dict_aa, dict_bb]
    returns [dict_a.update(dict_aa), dict_b.update(dict_bb)]
    """
    # TODO: find another way to merge all the dictionaries along the unique key so we don't need the assertion to be
    #  true
    assert len(dict_list1) == len(dict_list2)
    for i in range(len(dict_list1)):
        dict_list1[i].update(dict_list2[i])
    return dict_list1


def web_scraping():
    """
    This function is the main function. Running it is like running the file.
    """
    dicts_main = get_main()
    dicts_projects = get_project(get_urls(dicts_main))
    return join_lists_of_dicts(dicts_main, dicts_projects)


if __name__ == "__main__":
    merged_dicts = web_scraping()
    print()
