"""
This file, imported in web_scraping, creates the sql database based on a list of dictionaries with the scraped data
from freelancer.com.
"""
from cleaner import *
from globals import *
from api_currency import *
from api_related_skills import *
import sqlalchemy
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Boolean, Float
from sqlalchemy import create_engine
import pymysql.cursors
import os
import io
import pathlib
import json
import logging
from base_logger import logger

pymysql.install_as_MySQLdb()


def database_empty(database):
    """check if database not empy"""
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {database}")
    cursor.execute("SHOW FULL TABLES")
    my_list = cursor.fetchall()
    if my_list == ():
        return True
    return False


def instance_exists(table, inst, col='all', type='verification'):
    """check if inst (type str) already in table."""
    if col == 'all':
        col = '*'

    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute(f"SELECT {col} from {table};")
    my_list = cursor.fetchall()

    if type != 'verification':
        for a_dic in my_list:
            if inst in a_dic.values():
                return True
        return False
    else:
        for a_dic in my_list:
            if inst == [a_dic["mail"], a_dic["Payment"], a_dic["Deposit"]]:
                return True
        return False


def get_job_id(url):
    """
    Given a url (string) that exists in the database, get the associated job id in the sql database
    """
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute(f"""SELECT id FROM Job WHERE url = \'{url}\';""")
    return cursor.fetchone()['id']


def update_days_left(a_dict):
    """given an observation contained in a dictionary, update the value of days_left_to_bid"""
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")

    cursor.execute(f"""
    UPDATE Job 
    SET days_left_to_bid = {a_dict['days left to bid']} 
    WHERE url = \'{a_dict['url']}\';""")
    connection.commit()


def update_db(a_dict, competition_catalogue):
    """
    given an observation contained in a dictionary,
    update days_left_to_bid and competition_list in the sql database

    Used when job instance already exists
    """
    update_days_left(a_dict)
    competition_catalogue = add_competitor(a_dict, competition_catalogue)
    return competition_catalogue


def get_skill_description(skill, confidence_interval):
    """
    Given a skill name (string), returns a description of the skill using the Emsi api
    """
    access_token = create_access_token(my_client_id, my_client_secret, my_scope)

    results = get_skill_emsi(skill, confidence_interval, access_token)
    if results.shape[0] == 0:
        return ''
    else:
        return descriptions.append(results['skill.description'].tolist()[0])


def add_skill(a_dict, skill_catalogue):
    """
    given an observation contained in a dictionary,  update the tables Skill and SkillSet
    """

    table = 'Skill'
    job_id = get_job_id(a_dict['url'])

    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")

    for my_skill in [x.strip() for x in a_dict["skills"].split(',')]:

        check = instance_exists(table, my_skill, col='name', type='skill')

        if not check:
            # insert in sql db Skill table
            cursor.execute(f"""
            INSERT INTO {table} (name) 
            VALUES (\'{my_skill}\');""")

            connection.commit()

        # get id of existing skill
        cursor.execute(f"""
        SELECT id 
        FROM {table} 
        WHERE name = \'{my_skill}\';""")
        skill_id = cursor.fetchone()['id']

        # insert in sql db SkillSet table
        cursor.execute(f"""
            INSERT INTO SkillSet (job_id, skill_id) 
            VALUES (\'{job_id}\', \'{skill_id}\');""")
        connection.commit()

        if not check:
            skill_catalogue.append(my_skill)

    return skill_catalogue


def add_competitor(a_dict, competitor_urls):
    """
    given an observation contained in a dictionary, add or update the tables Competition and CompetitionSet
    and update the list competition_catalogue
    """

    table = 'Competition'

    # get job id
    job_id = get_job_id(a_dict['url'])

    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")

    for sub_dict in a_dict["competition_list"]:
        # check if competitor in catalogue
        check = instance_exists(table, sub_dict["url"], col='url', type='competition')

        if not check:
            # insert in sql db competition table
            cursor.execute(f"""
            INSERT INTO {table} (url, rating) 
            VALUES (\'{sub_dict["url"]}\', \'{sub_dict["rating"]}\');""")
            connection.commit()

        # get id of existing competitor
        cursor.execute(f"""
        SELECT id 
        FROM {table} 
        WHERE url = \'{sub_dict["url"]}\';""")
        competitor_id = cursor.fetchone()['id']

        # insert in sql db CompetitionSet table
        cursor.execute(f"""
            INSERT INTO CompetitionSet (job_id, Competition_id) 
            VALUES (\'{job_id}\', \'{competitor_id}\');""")
        connection.commit()

        if not check:
            # update competition_catalogue
            competitor_urls.append(sub_dict["url"])

    return competitor_urls


def add_verification(a_dict, verification_catalogue):
    """
    given an observation contained in a dictionary, update the sql database and verification_catalogue
    """
    my_verification = a_dict["verified_traits_list"]
    my_verification = list(map(lambda x: 1 if x else 0, my_verification))

    # check if verification triplet is in table Verification
    table = 'Verification'
    col = 'all'
    type = 'verification'
    check = instance_exists(table, my_verification, col, type)

    # get job id
    job_id = get_job_id(a_dict['url'])

    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(f"USE {DB_NAME}")

    if not check:
        # insert in sql db verification table
        cursor.execute(f"""
        INSERT INTO {table} (mail, Payment, Deposit) 
        VALUES (\'{my_verification[0]}\', \'{my_verification[1]}\', \'{my_verification[2]}\');""")
        connection.commit()

    # get id of verification triplet
    cursor.execute(f"""
    SELECT id 
    FROM {table} 
    WHERE mail = \'{my_verification[0]}\'
    AND Payment = \'{my_verification[1]}\'
    AND Deposit = \'{my_verification[2]}\'
    ;""")
    verification_id = cursor.fetchone()['id']

    # update VerificationSet table
    cursor.execute(f"""
        INSERT INTO VerificationSet (job_id, verification_id) 
        VALUES (\'{job_id}\', \'{verification_id}\');""")
    connection.commit()

    if not check:
        # save instance in verification_catalogue
        verification_catalogue.append(my_verification)

    return verification_catalogue


def add_instances(a_dict,
                  session,
                  Job,
                  Budget,
                  skill_catalogue,
                  competition_catalogue,
                  verification_catalogue):
    """given an observation contained in a dictionary, creates a new instance for each Class of the
    database, and creates an instance in the SQL database. """

    # job
    job = Job(title=a_dict["titles"],
              days_left_to_bid=a_dict["days left to bid"],
              job_description=a_dict["description"],
              url=a_dict["url"])

    session.add(job)
    session.commit()

    # add skill in catalogue
    skill_catalogue = add_skill(a_dict, skill_catalogue)

    # budget
    budget = Budget(Job=job,
                    currency_original=a_dict["currency"],
                    per_hour=a_dict["per_hour"] if a_dict["per_hour"] else None,
                    min_usd=a_dict["min_value"] if a_dict["min_value"] else None,
                    max_usd=a_dict["max_value"] if a_dict["max_value"] else None)

    session.add(budget)
    session.commit()

    # Competition
    competition_catalogue = add_competitor(a_dict, competition_catalogue)

    # verification
    verification_catalogue = add_verification(a_dict, verification_catalogue)

    return skill_catalogue, competition_catalogue, verification_catalogue


def create_tables(Base):
    """create tables (each class is a table)"""

    class Job(Base):
        __tablename__ = 'Job'

        id = Column(Integer, nullable=False, primary_key=True)
        title = Column(String(1000), nullable=False)
        days_left_to_bid = Column(Integer)
        job_description = Column(String(10000))
        url = Column(String(1000), nullable=False)

        Skillset = relationship("SkillSet", back_populates="Job")
        Budget = relationship("Budget", back_populates="Job")
        VerificationSet = relationship("VerificationSet", back_populates="Job")
        CompetitionSet = relationship("CompetitionSet", back_populates="Job")

    class SkillSet(Base):
        __tablename__ = 'SkillSet'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'))
        skill_id = Column(Integer, ForeignKey('Skill.id'))

        Job = relationship("Job", back_populates="Skillset")
        Skill = relationship("Skill", back_populates="Skillset")

    class Skill(Base):
        __tablename__ = 'Skill'

        id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
        name = Column(String(100))
        description = Column(String(10000))
        Skillset = relationship("SkillSet", back_populates="Skill")

    class Budget(Base):
        __tablename__ = 'Budget'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'))
        currency_original = Column(String(100))
        currency = Column(String(100))
        per_hour = Column(String(100))
        min_usd = Column(Integer)
        max_usd = Column(Integer)

        Job = relationship("Job", back_populates="Budget")

    class VerificationSet(Base):
        __tablename__ = 'VerificationSet'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)
        verification_id = Column(Integer, ForeignKey('Verification.id'))

        Job = relationship("Job", back_populates="VerificationSet")
        Verification = relationship("Verification", back_populates="VerificationSet")

    class Verification(Base):
        __tablename__ = 'Verification'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        mail = Column(Boolean)
        Payment = Column(Boolean)
        Deposit = Column(Boolean)

        VerificationSet = relationship("VerificationSet", back_populates="Verification")

    class CompetitionSet(Base):
        __tablename__ = 'CompetitionSet'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)
        Competition_id = Column(Integer, ForeignKey('Competition.id'))

        Job = relationship("Job", back_populates="CompetitionSet")
        Competition = relationship("Competition", back_populates="CompetitionSet")

    class Competition(Base):
        __tablename__ = 'Competition'

        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        url = Column(String(1000))
        rating = Column(Float)

        CompetitionSet = relationship("CompetitionSet", back_populates="Competition")

    return Job, SkillSet, Skill, Budget, VerificationSet, Verification, CompetitionSet, Competition


def get_catalogues():
    """
    extracts the catalogues from the file catalogues.json
    """
    path = str(pathlib.Path(__file__).parent.resolve())
    if os.path.getsize(path + '/catalogues.json') > 2:
        with open(path + "/catalogues.json", "r") as read_file:
            catalogues_att = json.load(read_file)

        skill_catalogue = catalogues_att['skill_catalogue']
        competition_catalogue = catalogues_att['competition_catalogue']
        verification_catalogue = catalogues_att['verification_catalogue']

    else:
        skill_catalogue = []
        competition_catalogue = []
        verification_catalogue = []

    return skill_catalogue, competition_catalogue, verification_catalogue


def save_json(skill_catalogue, competition_catalogue, verification_catalogue):
    """Given 3 lists, turns the lists into a dictionary and save it in a json file"""

    dict_json = {'skill_catalogue': skill_catalogue,
                 'competition_catalogue': competition_catalogue,
                 'verification_catalogue': verification_catalogue}

    path = str(pathlib.Path(__file__).parent.resolve())

    with open(path + "/catalogues.json", "w") as write_file:
        json.dump(dict_json, write_file)
    logger.info('saved catalogues in file catalogues.json')


def insert_values(db_empty,
                  a_dict,
                  session,
                  Job,
                  Budget,
                  skill_catalogue,
                  competition_catalogue,
                  verification_catalogue):
    """
    insert observation in sql db
    """
    if db_empty:
        if instance_exists('Job', a_dict["url"], 'url', type='job'):
            competition_catalogue = update_db(a_dict, competition_catalogue)
        else:
            skill_catalogue, competition_catalogue, verification_catalogue = add_instances(a_dict,
                                                                                           session,
                                                                                           Job,
                                                                                           Budget,
                                                                                           skill_catalogue,
                                                                                           competition_catalogue,
                                                                                           verification_catalogue)
    else:
        skill_catalogue, competition_catalogue, verification_catalogue, = add_instances(a_dict,
                                                                                        session,
                                                                                        Job,
                                                                                        Budget,
                                                                                        skill_catalogue,
                                                                                        competition_catalogue,
                                                                                        verification_catalogue)
    logger.info('added or updated 1 instance to the SQL database freelancer')
    return skill_catalogue, competition_catalogue, verification_catalogue


def db_initialization(engine, Base):
    """
    If the data base does not exist, create it and clean the json file of catalogues
    """

    db_empty = database_empty(DB_NAME)
    engine.execute(f"USE {DB_NAME}")
    Base.metadata.create_all(engine)
    if db_empty:
        # clean catalogues.json
        path = str(pathlib.Path(__file__).parent.resolve())
        with open(path + '/catalogues.json', 'w') as fp:
            json.dump({}, fp)
            logger.info('Created file catalogues.json')
    return db_empty


def enrich_api():
    # add description to skills in table Skill via IPA
    skill_descriptions_to_sql()
    logger.info('enriched the skill table with skill description using the EMSI API')

    # convert all currencies/values to USD
    enrich_budget_currency()
    logger.info('enriched the budget table with dollar currency conversion using exchangerate API')


def create_sql(dict_merged):
    """
    Given dict_merged, a list of dictionaries with the scraped data from freelancer.com,
    the function creates or updates a sql database .

    Each class is a table in the database.

    Possibility to update the database if it already exists.
    It updates the existing instances with new values, or adds new instances to the database.
    """
    # clean dictionaries
    dict_merged = cleaner(dict_merged)

    # initialize engine
    engine = sqlalchemy.create_engine(f'mysql://{USERNAME}:{PASSWORD}@{HOST}')  # connect to server

    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    # create tables (each class is a table)
    Job, SkillSet, Skill, Budget, VerificationSet, Verification, CompetitionSet, Competition = create_tables(Base)

    # create db if does not exist, use the existing one otherwise
    db_empty = db_initialization(engine, Base)

    # if the db exists, the catalogues too. We load them:
    skill_catalogue, competition_catalogue, verification_catalogue = get_catalogues()

    # insert values from dict_merged
    for a_dict in dict_merged:
        skill_catalogue, competition_catalogue, verification_catalogue = insert_values(db_empty,
                                                                                       a_dict,
                                                                                       session,
                                                                                       Job,
                                                                                       Budget,
                                                                                       skill_catalogue,
                                                                                       competition_catalogue,
                                                                                       verification_catalogue)

    logger.info('added instances / updated instances to the SQL database freelancer')

    # save catalogues in json file (catalogues.json)
    save_json(skill_catalogue, competition_catalogue, verification_catalogue)

    # enrich SKill and Budget with APIs
    #enrich_api()

    session.close()
