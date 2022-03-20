"""
This file, imported in web_scraping, creates the sql database based on a list of dictionaries with the scraped data
from freelancer.com.
"""
from cleaner import *
from globals import *

import sqlalchemy
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Boolean, Float
from sqlalchemy import create_engine
import pymysql
from sqlalchemy import create_engine
import pymysql.cursors

pymysql.install_as_MySQLdb()
DB_NAME = "freelancer"


def database_exists(database):
    """check if database exists"""
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()  # get the cursor
    cursor.execute("SHOW DATABASES")
    my_list = cursor.fetchall()
    for a_dic in my_list:
        if database in a_dic.values():
            return True
    return False


def instance_exists_url(url, table):
    """check if job already in database. We check with the url, which is unique"""
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()  # get the cursor
    cursor.execute(f"USE freelancer")
    cursor.execute(f"SELECT url from {table};")
    my_list = cursor.fetchall()
    for a_dic in my_list:
        if url in a_dic.values():
            return True
    return False


def update_db(a_dict, url):
    """update days_left_to_bid and competition_list in the sql database"""
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()  # get the cursor
    cursor.execute(f"USE {DB_NAME}")
    # update days_left_to_bid
    cursor.execute(f"UPDATE Job SET days_left_to_bid = {a_dict['days left to bid']} WHERE url = \'{url}\';")
    connection.commit()

    # update Competition and CompetitionSet
    # get job id
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()  # get the cursor
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute(f"""SELECT id FROM Job WHERE url = \'{url}\';""")
    job_id = cursor.fetchone()['id']
    # print("job id: ", job_id)

    # Competition
    urls = []
    ratings = []
    for another_dict in a_dict["competition_list"]:
        urls.append(another_dict["url"])
        ratings.append(another_dict["rating"])

    # add if competitor url is not in the list
    for my_url, my_rating in zip(urls, ratings):
        if not instance_exists_url(my_url, "Competition"):
            connection = pymysql.connect(host=HOST,
                                         user=USERNAME,
                                         password=PASSWORD,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute(f"""INSERT INTO Competition (url, rating) VALUES (\'{my_url}\', \'{my_rating}\');""")
            cursor.execute(f"""SELECT id FROM Competition WHERE url = \'{my_url}\';""")
            competitor_id = cursor.fetchone()['id']
            # connection.commit()

            # CompetitionSet
            cursor.execute(
                f"""INSERT INTO CompetitionSet (job_id, Competition_id) VALUES (\'{job_id}\', \'{competitor_id}\');""")
            connection.commit()


def add_instances(a_dict, session, Job, SkillSet, Skill, Budget, VerificationSet, Verification, CompetitionSet,
                  Competition, skill_catalogue, verification_catalogue, competition_catalogue):
    """given a dictionary instance, create a new instance in the SQL database"""

    # job
    job = Job(title=a_dict["titles"],
              days_left_to_bid=a_dict["days left to bid"],
              job_description=a_dict["description"],
              url=a_dict["url"])

    session.add(job)
    # add skill in catalogue
    for my_skill in [x.strip() for x in a_dict["skills"].split(',')]:
        if any(x for x in skill_catalogue if x.name == my_skill):
            skill = [x for x in skill_catalogue if x.name == my_skill]
            skill_set = SkillSet(Job=job, Skill=skill[0])
            session.add(skill_set)
        else:
            skill = Skill(name=my_skill)
            skill_catalogue.add(skill)
            skill_set = SkillSet(Job=job, Skill=skill)
            session.add(skill)
            session.add(skill_set)

    # budget
    budget = Budget(Job=job,
                    currency=a_dict["currency"],
                    per_hour=a_dict["per_hour"],
                    min=a_dict["min_value"],
                    max=a_dict["max_value"])
    session.add(budget)

    # Competition
    for my_comp in a_dict["competition_list"]:
        if any(x for x in competition_catalogue if x.url == my_comp['url']):
            comp = [x for x in competition_catalogue if x.url == my_comp['url']]
            comp_set = CompetitionSet(Job=job, Competition=comp[0])
            session.add(comp_set)
        else:
            comp = Competition(url=my_comp['url'], rating=my_comp['rating'])
            competition_catalogue.add(comp)
            comp_set = CompetitionSet(Job=job, Competition=comp)
            session.add(comp)
            session.add(comp_set)

    # verification
    if any(x for x in verification_catalogue if
           [x.mail, x.Payment, x.Deposit] == a_dict["verified_traits_list"]):
        verification = [x for x in verification_catalogue if
                        [x.mail, x.Payment, x.Deposit] == a_dict["verified_traits_list"]]
        verification_set = VerificationSet(Job=job, Verification=verification[0])
        session.add(verification_set)
    else:
        verification = Verification(mail=a_dict["verified_traits_list"][0],
                                    Payment=a_dict["verified_traits_list"][1],
                                    Deposit=a_dict["verified_traits_list"][2])
        verification_set = VerificationSet(Job=job, Verification=verification)
        verification_catalogue.add(verification)
        session.add(verification)
        session.add(verification_set)

    return skill_catalogue, verification_catalogue, competition_catalogue


def create_sql(dict_merged):
    """
    Given dict_merged, a list of dictionaries with the scraped data from freelancer.com,
    the function creates a sql database freelancer
    Each class is a table in the database.
    """
    # clean dictionaries
    dict_merged = cleaner(dict_merged)

    # initialize database
    username = USERNAME
    password = PASSWORD
    host = HOST
    engine = sqlalchemy.create_engine(f'mysql://{username}:{password}@{host}')  # connect to server

    # create db if does not exist
    db_exist = database_exists(DB_NAME)
    if not db_exist:
        engine.execute(f"CREATE DATABASE {DB_NAME}")  # create db

    engine.execute(f"USE {DB_NAME}")

    # start session
    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    # create tables (each class is a table)
    class Job(Base):
        __tablename__ = 'Job'

        # Initialize the Column
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
        __tablename__ = 'Skillset'

        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'))
        skill_id = Column(Integer, ForeignKey('Skill.id'))

        # Initialize the relationship
        Job = relationship("Job", back_populates="Skillset")
        Skill = relationship("Skill", back_populates="Skillset")

    class Skill(Base):
        __tablename__ = 'Skill'

        # Initialize the Column
        id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
        name = Column(String(100))
        Skillset = relationship("SkillSet", back_populates="Skill")

    class Budget(Base):
        __tablename__ = 'Budget'

        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'))
        currency = Column(String(100))
        per_hour = Column(String(100))
        min = Column(Integer)
        max = Column(Integer)

        # Initialize the relationship
        Job = relationship("Job", back_populates="Budget")

    class VerificationSet(Base):
        __tablename__ = 'VerificationSet'

        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)
        verification_id = Column(Integer, ForeignKey('Verification.id'))

        # Initialize the relationship
        Job = relationship("Job", back_populates="VerificationSet")
        Verification = relationship("Verification", back_populates="VerificationSet")

    class Verification(Base):
        __tablename__ = 'Verification'

        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        mail = Column(Boolean)
        Payment = Column(Boolean)
        Deposit = Column(Boolean)

        # Initialize the relationship
        VerificationSet = relationship("VerificationSet", back_populates="Verification")

    class CompetitionSet(Base):
        __tablename__ = 'CompetitionSet'

        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)
        Competition_id = Column(Integer, ForeignKey('Competition.id'))

        # Initialize the relationship
        Job = relationship("Job", back_populates="CompetitionSet")
        Competition = relationship("Competition", back_populates="CompetitionSet")

    class Competition(Base):
        __tablename__ = 'Competition'

        # Initialize the Column (there should be 9 lines in this table
        id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
        url = Column(String(1000))
        rating = Column(Float)

        # Initialize the relationship
        CompetitionSet = relationship("CompetitionSet", back_populates="Competition")

    if not db_exist:
        Base.metadata.create_all(engine)

    skill_catalogue = set()
    verification_catalogue = set()
    competition_catalogue = set()

    # insert values from dict_merged
    for a_dict in dict_merged:
        if db_exist:  # if  db existed, update if instance existed, create otherwise
            # check if instance already exists
            instance_exist = instance_exists_url(a_dict["url"], "Job")
            if instance_exist:
                update_db(a_dict, a_dict["url"])
            else:
                skill_catalogue, verification_catalogue, competition_catalogue = add_instances(a_dict, session, Job,
                                                                                               SkillSet, Skill, Budget,
                                                                                               VerificationSet,
                                                                                               Verification,
                                                                                               CompetitionSet,
                                                                                               Competition,
                                                                                               skill_catalogue,
                                                                                               verification_catalogue,
                                                                                               competition_catalogue)
        else:
            skill_catalogue, verification_catalogue, competition_catalogue = add_instances(a_dict, session, Job,
                                                                                           SkillSet, Skill, Budget,
                                                                                           VerificationSet,
                                                                                           Verification,
                                                                                           CompetitionSet, Competition,
                                                                                           skill_catalogue,
                                                                                           verification_catalogue,
                                                                                           competition_catalogue)
    # Insert to the database
    session.commit()
    session.close()

