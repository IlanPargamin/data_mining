import re


def cleaner(dict_merged):
    dict_merged = clean_budget(dict_merged)
    dict_merged = clean_days_left(dict_merged)
    dict_merged = clean_skills(dict_merged)
    return dict_merged


def clean_skills(dict_merged):
    """
    If the object is None in the value associated with the value "skills", we modify None to an empty string
    """
    for my_dict in dict_merged:
        if "skills" in my_dict and not my_dict["skills"]:
            my_dict["skills"] = ''
    return dict_merged


def clean_budget(dict_merged):
    """

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
    for my_dict in dict_merged:
        match = re.search(r'[0-9]', my_dict['days left to bid'])
        if match:
            my_dict['days left to bid'] = int(match.group(0))
        else:
            my_dict['days left to bid'] = None
    return dict_merged


if __name__ == "__main__":
    dict_merged = {"budget": "9"}
    dict_merged = cleaner(dict_merged)
    dict_merged = clean_budget(dict_merged)
