import re
import pandas as pd
import csv
# TODO clean
# TODO write docstrings
def clean_ilan(dict_merged):
    """

    """
    dict_merged = index_jobs(dict_merged)
    dict_merged = clean_verified_traits(dict_merged)
    dict_merged = clean_skills(dict_merged)
    dict_merged = clean_budget(dict_merged)
    dict_merged = clean_days_left(dict_merged)
    return dict_merged

def index_jobs(dict_merged):
    id = 1
    for my_dict in dict_merged:
        my_dict["id"] = id
        id += 1
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
            match = re.search(r'[0-9]+\-[0-9]+', my_dict['budget'])
            if match:
                my_dict['min_value'] = match.group(0).split("-")[0]
                my_dict['max_value'] = match.group(0).split("-")[1]
            if "hour" in my_dict['budget']:
                my_dict['per_hour'] = True
            else:
                my_dict['per_hour'] = False

    return dict_merged


def clean_skills(dict_merged):
    """
    """


    # add in the dicts a list of each skill
    all_skills = {"PDF"}
    for my_dict in dict_merged:
        if 'skills' in my_dict and my_dict['skills']:
            for each_skill in my_dict['skills'].split(","):
                all_skills.add(each_skill.strip())

    id = 1
    skills_id = {}
    for skill in all_skills:
        skills_id[skill] = [id]
        id += 1

    for my_dict in dict_merged:
        for skill in all_skills:
            if my_dict["skills"]:
                if skill in my_dict["skills"]:
                    my_dict[skill] = skills_id[skill][0]

    # we keep the dictionary element-id in a csv file. We will need it to build the sql database
    df = pd.DataFrame.from_dict(skills_id)
    df.to_csv(r'skills_id.csv', index=False, header=True)

    # we export to a csv file the data we will need
    your_keys = list(all_skills)
    dict_export = []
    for my_dict in dict_merged:
        dict_export.append({k: v for k, v in my_dict.items() if k in your_keys})

    keys = list(all_skills)
    with open('skills.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict_export)

    df_skill = pd.read_csv(r'skills.csv', delimiter=',')
    df_skill.index += 1
    df_skill = df_skill.stack(dropna=True).to_frame()
    df_skill = df_skill.reset_index()
    df_skill = df_skill.rename(columns={"level_0": "index", "level_1": "element", 0: "element_id"})
    # rename columns
    df_skill.to_csv('skills.csv')


    return dict_merged


# days left to bid
def clean_days_left(dict_merged):
    for my_dict in dict_merged:
        my_dict['days left to bid'] = int(re.search(r'[0-9]', my_dict['days left to bid']).group(0))
    return dict_merged


def clean_verified_traits(dict_merged):
    """

    """
    # get all traits
    traits = {"E-mail Verified", "Payment Verified", "Made a Deposit"}
    traits_id = {}
    id = 1
    for trait in traits:
        traits_id[trait] = [id]
        id += 1

    for my_dict in dict_merged:
        for trait in traits:
            if trait in my_dict["verified_traits_list"]:
                my_dict[trait] = traits_id[trait][0]
            else:
                my_dict[trait] = None

    # we keep the dictionary element-id in a csv file. We will need it to build the sql database
    df = pd.DataFrame.from_dict(traits_id)
    df.to_csv(r'traits_id.csv', index=False, header=True)

    # we export to a csv file the data we will need
    your_keys = ['Payment Verified', 'Made a Deposit', 'E-mail Verified']
    dict_export = []
    for my_dict in dict_merged:
        dict_export.append({k: v for k, v in my_dict.items() if k in your_keys})

    keys = dict_export[0].keys()
    with open('verifications.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dict_export)

    df_verif = pd.read_csv(r'verifications.csv', delimiter=',')
    df_verif.index += 1
    df_verif = df_verif.stack(dropna=False).to_frame()
    df_verif = df_verif.reset_index()
    df_verif = df_verif.rename(columns={"level_0": "index", "level_1": "element", 0: "element_id"})
    # rename columns
    df_verif.to_csv('verifications.csv', index=False)
    return dict_merged


if __name__ == "__main__":
    # clean_ilan(dict_merged)
    print()
