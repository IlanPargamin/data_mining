"""
This file, imported in web_scraping, creates the sql database based on a list of dictionaries with the scraped data
from freelancer.com.
"""

import sqlalchemy
from cleaner import *
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Boolean, Float
from sqlalchemy import create_engine
import pymysql
from globals import *
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

pymysql.install_as_MySQLdb()


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
    DB_NAME = 'freelancer'

    engine = sqlalchemy.create_engine(f'mysql://{username}:{password}@{host}')  # connect to server

    if not database_exists(engine.url):
        engine.execute(f"CREATE DATABASE {DB_NAME}")  # create db
    engine.execute(f"USE {DB_NAME}")

    Session = sessionmaker(bind=engine)
    session = Session()

    Base = declarative_base()

    skill_catalogue = set()
    verification_catalogue = set()
    competition_catalogue = set()

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

    Base.metadata.create_all(engine)

    # insert values from dict_merged
    for a_dict in dict_merged:
        # job
        job = Job(title=a_dict["titles"],
                  days_left_to_bid=a_dict["days left to bid"],
                  job_description=a_dict["description"],
                  url=a_dict["url"])

        session.add(job)
        if_stop = 1
        # add skill in catalogue
        for my_skill in [x.strip() for x in a_dict["skills"].split(',')]:
            if any(x for x in skill_catalogue if x.name == my_skill):
                skill = [x for x in skill_catalogue if x.name == my_skill]
                skill_set = SkillSet(Job=job, Skill=skill[0])
                session.add(skill_set)
                if_stop += 1
            if if_stop == 2:
                session.commit()
                session.close()
                exit()
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
        if any(x for x in verification_catalogue if [x.mail, x.Payment, x.Deposit] == a_dict["verified_traits_list"]):
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

    # Insert to the database
    session.commit()
    print("Output extracted in the freelancer sql database.")
    session.close()
