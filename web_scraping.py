"""
main file
To choose the range of the pages to scrape, you can modify the global variables in the file globals.py
"""
# TODO write log file

from get_main import get_main
from get_urls import get_urls
from get_project import get_project
from clean import clean_ilan
import logging
import argparse
import csv
import sys

# def setup_logger(name, log_file, level=logging.INFO):
#     """
#     To setup as many loggers as needed
#     """
#
#     handler = logging.FileHandler(log_file)
#     handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
#
#     a_logger = logging.getLogger(name)
#     a_logger.setLevel(level)
#     a_logger.addHandler(handler)
#
#     return a_logger
#
#
# stdout = setup_logger('stdout', 'stdout.log')


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


def export_to_csv(list_of_dicts):
    """
    export a list of dictionaries to a csv file
    """
    keys = list_of_dicts[0].keys()
    with open('output.csv', 'w', newline='') as output_file:
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
        # stdout.info(merged_dic)
        return merged_dic
    else:
        # stdout.info(dicts_main)
        print(f"main page only")
        return dicts_main


def page2page(page_start, page_stop):
    """
    modify our globals by print the terminal arguments in the file globals.py
    """
    file_path = 'globals.py'
    with open(file_path, 'w') as f:
        f.write(f"""MAIN_URL = 'https://www.freelancer.com'\nPAGE_START = {page_start}\nPAGE_STOP = {page_stop}""")


def my_parser():
    """
    parses the arguments from the command line
    User must input the pages range she wants to scrape (page_start and page_stop).
    If the user does not want details on the projects (i.e. collect what the function get_project returns) then
    she must add -not in the console command.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('page_start')
    parser.add_argument('page_stop')
    parser.add_argument('-not', '--no_scrape_all', action='store_true')
    parser.add_argument('-clean', '--clean_ilan', action='store_true')
    args = parser.parse_args()


    if not args.page_start.isdigit() or not args.page_stop.isdigit():
        print(f'input must be digit')
        sys.exit(1)


    if int(args.page_start) > int(args.page_stop):
        print("The starting page must be lower than the last page")
        sys.exit(1)

    print(f"scraping freelancer.com/jobs from page {args.page_start} to page {args.page_stop} ")
    if args.no_scrape_all:
        run_get_project = False
    else:
        run_get_project = True

    page2page(args.page_start, args.page_stop)
    if args.clean_ilan:
        export_to_csv(clean_ilan(web_scraping(run_get_project)))
    else:
        export_to_csv(web_scraping(run_get_project))

    print("Output extracted in the output.csv file.")


if __name__ == "__main__":
    my_parser()
    #dict_merged = web_scraping(run_get_project=True)
    #dict_merged = clean_ilan(dict_merged)

