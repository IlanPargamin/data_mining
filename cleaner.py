"""
The cleaner file.
Cleans the list of dictionaries raw data.

"""


import re


def cleaner(dict_merged):
    """
    main cleaner
    """
    dict_merged = clean_budget(dict_merged)
    dict_merged = clean_days_left(dict_merged)
    dict_merged = clean_skills(dict_merged)
    dict_merged = clean_description(dict_merged)
    dict_merged = clean_verification(dict_merged)
    return dict_merged


def clean_skills(dict_merged):
    """
    If the object is None in the value associated with the value "skills", we modify None to an empty string
    """
    for my_dict in dict_merged:
        if "skills" in my_dict and not my_dict["skills"]:
            my_dict["skills"] = ''
        if "skills" not in my_dict:
            my_dict["skills"] = ''
    return dict_merged


def clean_budget(dict_merged):
    """
    Given a list of dictionaries which have each a key "budget" associated with information on currency,
    a range àf digits and a type of price (per hour or not), splits the string into sub categories and
    inserts them in the given dictionaries.

    Example :  "$10-15 USD per hour"  #(my_dict['budget'])
    becomes:
    my_dict['currency'] = "USD"
    my_dict['min_value'] = 10
    my_dict['max_value'] = 15
    my_dict['per_hour'] = True

    Inserts None if no match.

    """
    for my_dict in dict_merged:
        # get currency
        if 'budget' in my_dict and my_dict['budget']:
            match = re.search(r'[A-Z]{3}', my_dict['budget'])
            if match:
                my_dict['currency'] = match.group(0)
            else:
                my_dict['currency'] = None
            match = re.search(r'[0-9]+\-[0-9]+', my_dict['budget'])

            if match:
                my_dict['min_value'] = match.group(0).split("-")[0]
                my_dict['max_value'] = match.group(0).split("-")[1]
            else:
                my_dict['min_value'] = None
                my_dict['max_value'] = None

            if "hour" in my_dict['budget']:
                my_dict['per_hour'] = True
            else:
                my_dict['per_hour'] = False
        else:
            my_dict['currency'] = None
            my_dict['min_value'] = None
            my_dict['max_value'] = None
            my_dict['per_hour'] = None

    return dict_merged


def clean_days_left(dict_merged):
    """
    Given a list of dictionaries which have each a key "days left to bid" associated with information on the number of
    days left to bid, we extract the exact number of day and turn it into an integer. We replace the value associated
    with the key 'days left to bid'.

    Replaces the value with None if no digit found.
    """
    for my_dict in dict_merged:
        match = re.search(r'[0-9]', my_dict['days left to bid'])
        if match:
            my_dict['days left to bid'] = int(match.group(0))
        else:
            my_dict['days left to bid'] = None
    return dict_merged


def clean_description(dict_merged):
    """
    if missing value, we add a list with an empty string
    """
    for my_dict in dict_merged:
        if "description" not in my_dict:
            my_dict["description"] = ""
    return dict_merged


def clean_verification(dict_merged):
    """
    if missing value, we add a list with an empty string
    """
    for my_dict in dict_merged:
        if "verified_traits_list" not in my_dict:
            my_dict["verified_traits_list"] = ""
    return dict_merged
