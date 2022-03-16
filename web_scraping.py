"""
main file
To choose the range of the pages to scrape, you can modify the global variables in the file globals.py
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
        print(f"including project pages")
        dicts_projects = get_project(get_urls(dicts_main))
        merged_dic = join_lists_of_dicts(dicts_main, dicts_projects)
        return merged_dic
    else:
        print(f"main page only")
        return dicts_main


def page2page(page_start, page_stop):
    """
    modify our globals by printing the terminal arguments in the file globals.py
    """
    file_path = 'globals.py'
    with open(file_path, 'w') as f:
        f.write(f"""MAIN_URL = 'https://www.freelancer.com'\nPAGE_START = {page_start}\nPAGE_STOP = {page_stop}""")


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

    # TODO add test: if directory_path does not exist


def my_parser():
    """
    parses the arguments from the command line
    User must input the pages range she wants to scrape (page_start and page_stop).
    If the user does not want details on the projects (i.e. collect what the function get_project returns) then
    she must add -not in the console command.
    User can choose to export to csv file or to sql database (format .db)
    """

    # design parser
    parser = argparse.ArgumentParser(epilog=textwrap.dedent('''\
         additional information:
             If neither -tocsv nor -csv are specified, the scraper does not export the data to any file
         '''))
    parser.add_argument('page_start')
    parser.add_argument('page_stop')
    parser.add_argument('directory_path')
    parser.add_argument('-not', '--no_scrape_all', action='store_true',
                        help="collect titles, urls and number of days left to bid only")
    parser.add_argument('-tosql', '--tosql', action='store_true', help="export to freelancer.db ")
    parser.add_argument('-tocsv', '--tocsv', action='store_true', help="export to freelancer.csv ")
    args = parser.parse_args()

    # test validity of arguments
    test_valid_arguments(args)

    if args.no_scrape_all:
        run_get_project = False
    else:
        run_get_project = True

    # scrape
    print(f"scraping freelancer.com/jobs from page {args.page_start} to page {args.page_stop} ")
    page2page(args.page_start, args.page_stop)
    dict_merged = web_scraping(run_get_project)

    # export data
    if args.tosql:
        create_sql(dict_merged, args.directory_path)
        print(f"Output extracted in the freelancer.db database in the directory {args.directory_path}.")

    if args.tocsv:
        dict_merged = cleaner(dict_merged)
        export_to_csv(dict_merged, args.directory_path)
        print(f"Data exported to file freelancer.csv in the directory {args.directory_path}")


if __name__ == "__main__":
    my_parser()
