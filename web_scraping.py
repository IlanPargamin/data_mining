"""
usage: web_scraping.py [-h] [-not] [-tosql]
                       page_start page_stop sql_username sql_password sql_host

positional arguments:
  page_start            Scraping will start from this page
  page_stop             Scraping will stop at this page
  sql_username          Your sql username (commonly 'root')
  sql_password          Your sql password
  sql_host              Your sql hostname (commonly 'localhost')

optional arguments:
  -h, --help            show this help message and exit
  -tosql, --tosql       export to freelancer sql database

additional information: The main url is "freelancer.com"
"""

from get_main import get_main
from get_urls import get_urls
from get_project import get_project
from build_sql import create_sql
from cleaner import cleaner
import logging
import argparse
import csv
import sys
import textwrap


def setup_logger(name, log_file, level=logging.INFO):
    """
    To setup as many loggers as needed
    """

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    a_logger = logging.getLogger(name)
    a_logger.setLevel(level)
    a_logger.addHandler(handler)

    return a_logger


# stdout = setup_logger('stdout', 'stdout.log')
# TODO write log file


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


def export_to_csv(list_of_dicts, directory_path):
    """
    NOT USED
    export a list of dictionaries to a csv file
    creates the file if it does not exist
    """
    keys = list_of_dicts[0].keys()
    with open(directory_path + '/freelancer.csv', 'w+', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dicts)


def web_scraping(run_get_project=True):
    """
    This function is the main function. It returns a list of dictionaries where each dictionary contains data on a
    specific job offer from freelancer.com.
    If run_get_project=True, we run the function get_project and collect more detailed data on each project.
    """
    dicts_main = get_main()
    if run_get_project:
        print(f"Including project pages")
        dicts_projects = get_project(get_urls(dicts_main))
        merged_dic = join_lists_of_dicts(dicts_main, dicts_projects)
        return merged_dic
    else:
        print(f"Main page only")
        return dicts_main


def modify_globals(page_start, page_stop, sql_username, sql_password, sql_host):
    """
    modify our globals by printing the terminal arguments in the file globals.py
    """
    file_path = 'globals.py'
    with open(file_path, 'w') as f:
        f.write(f"""MAIN_URL = 'https://www.freelancer.com'\nPAGE_START = {page_start}\nPAGE_STOP = {page_stop}\
\nUSERNAME = \'{sql_username}\'\nPASSWORD = \'{sql_password}\'\nHOST = \'{sql_host}\'""")


def test_valid_arguments(args):
    """
    Exit if parsed arguments are not valid
    """
    if not args.page_start.isdigit() or not args.page_stop.isdigit():
        print(f'input must be digit')
        sys.exit(1)

    if int(args.page_start) > int(args.page_stop):
        print("The starting page must be lower than the last page")
        sys.exit(1)


def my_parser():
    """
    parses the arguments from the command line and call the scraper
    """

    # design parser
    parser = argparse.ArgumentParser(epilog=textwrap.dedent('''\
         additional information:
             The main url is "freelancer.com"
         '''))
    parser.add_argument('page_start', help="Scraping will start from this page")
    parser.add_argument('page_stop', help="Scraping will stop at this page")
    parser.add_argument('sql_username', help="Your sql username (commonly 'root')")
    parser.add_argument('sql_password', help="Your sql password")
    parser.add_argument('sql_host', help="Your sql hostname (commonly 'localhost')")
    # parser.add_argument('-not', '--no_scrape_all', action='store_true',
    #                     help="collect titles, urls and number of days left to bid only")
    parser.add_argument('-tosql', '--tosql', action='store_true', help="export to freelancer sql database ")
    args = parser.parse_args()

    # test validity of arguments
    test_valid_arguments(args)

    # if args.no_scrape_all:
    #     run_get_project = False
    # else:
    #     run_get_project = True

    # scrape
    print(f"scraping freelancer.com/jobs from page {args.page_start} to page {args.page_stop} ")
    modify_globals(args.page_start, args.page_stop, args.sql_username, args.sql_password, args.sql_host)
    dict_merged = web_scraping(run_get_project=True)

    # export data
    if args.tosql:
        create_sql(dict_merged)
        print(f"Output extracted in the freelancer sql database.")


if __name__ == "__main__":
    my_parser()
