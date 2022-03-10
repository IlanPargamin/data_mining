import re

# TODO clean
# TODO write docstrings
def clean_ilan(dict_merged):
    """

    """
    dict_merged = clean_verified_traits(dict_merged)
    dict_merged = clean_skills(dict_merged)
    dict_merged = clean_budget(dict_merged)
    dict_merged = clean_days_left(dict_merged)
    return dict_merged


def clean_budget(dict_merged):
    """

    """
    for my_dict in dict_merged:
        # get currency
        if 'budget' in my_dict and my_dict['budget']:
            currency = re.search(r'[A-Z]{3}', my_dict['budget']).group(0)
            amount = re.search(r'[0-9]+\-[0-9]+', my_dict['budget']).group(0)
            if "hour" in my_dict['budget']:
                per_hour = "per_hour"
            else:
                per_hour = "range"
            my_dict["budget"] = (currency, amount, per_hour)

    return dict_merged


def clean_skills(dict_merged):
    """
    """
    ## add in all dicts a list of all skills' id
    all_skills = {""}
    for my_dict in dict_merged:
        if 'skills' in my_dict and my_dict['skills']:
            for skill in my_dict['skills'].split(","):
                all_skills.add(skill)

    ## add ID to each skill
    skill_ids = {}
    for skill in all_skills:
        skill_ids[skill] = id(skill)

    ## add in the dicts a list of each (skill, id)
    for my_dict in dict_merged:
        if 'skills' in my_dict and my_dict['skills']:
            my_dict['skills_and_id'] = []
            for each_skill in my_dict['skills'].split(","):
                my_dict['skills_and_id'].append((each_skill, (lambda x: skill_ids[x])(each_skill)))
            my_dict['skills'] = my_dict.pop('skills_and_id')
    return dict_merged


# days left to bid
def clean_days_left(dict_merged):
    for my_dict in dict_merged:
        my_dict['days left to bid'] = int(re.search(r'[0-9]', my_dict['days left to bid']).group(0))
    return dict_merged


def clean_verified_traits(dict_merged):
    """

    """
    verified_traits = {'email_verified', 'payment_verified', 'deposit_verified'}
    traits_id = {}
    for skill in verified_traits:
        traits_id[skill] = id(skill)

    for my_dict in dict_merged:
        if 'verified_traits_list' in my_dict:
            if 'E-mail Verified' in my_dict['verified_traits_list']:
                email = ('email_verified', (lambda x: traits_id[x])('email_verified'))
            else:
                email = None
            if 'Payment Verified' in my_dict['verified_traits_list']:
                payment = ('payment_verified', (lambda x: traits_id[x])('payment_verified'))
            else:
                payment = None
            if 'Made a Deposit' in my_dict['verified_traits_list']:
                deposit = ('deposit_verified', (lambda x: traits_id[x])('deposit_verified'))
            else:
                deposit = None
            my_dict['verified_traits_list'] = (email, payment, deposit)
    return dict_merged


if __name__ == "__main__":
    #clean_ilan(dict_merged)
    print()
