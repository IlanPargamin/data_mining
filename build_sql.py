"""
This file, imported in web_scraping, creates the sql database based on a list of dictionaries with the scraped data
from freelancer.com.
"""

import sqlalchemy
from cleaner import *
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy import create_engine
import pymysql

pymysql.install_as_MySQLdb()


def create_sql(dict_merged, directory_path):
    """
    Given dict_merged, a list of dictionaries with the scraped data from freelancer.com, and a dicrectory path,
    the function creates a sql database freelancer.db in the given directory.
    Each class is a table in the database.
    """
    # clean dictionaries
    dict_merged = cleaner(dict_merged)

    # initialize database
    username = 'root'
    password = 'erssd9Af'
    host = 'localhost'
    port = 3306
    DB_NAME = 'freelancer'

    engine = sqlalchemy.create_engine(f'mysql://{username}:{password}@{host}')  # connect to server
    engine.execute(f"CREATE DATABASE {DB_NAME}")  # create db
    engine.execute(f"USE {DB_NAME}")

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

    class SkillSet(Base):
        __tablename__ = 'SkillSet'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = relationship('Job', backref=backref('SkillSet', lazy=True))

    class Skill(Base):
        __tablename__ = 'Skill'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        skill_set_id = Column(Integer, ForeignKey('SkillSet.id'), nullable=False)
        name = Column(String(100))

        # Initialize the relationship
        skillset = relationship('SkillSet', backref=backref('Skill', lazy=True))

    class BudgetSet(Base):
        __tablename__ = 'BudgetSet'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = relationship('Job', backref=backref('BudgetSet', lazy=True))

    class BudgetInfo(Base):
        __tablename__ = 'BudgetInfo'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        budgets_id = Column(Integer, ForeignKey('BudgetSet.id'), nullable=False)
        currency = Column(String(100))
        per_hour = Column(String(100))
        min = Column(Integer)
        max = Column(Integer)

        # Initialize the relationship
        budget_set = relationship('BudgetSet', backref=backref('BudgetInfo', lazy=True))

    class VerificationSet(Base):
        __tablename__ = 'VerificationSet'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = relationship('Job', backref=backref('VerificationSet', lazy=True))

    class Verification(Base):
        __tablename__ = 'Verification'
        # Initialize the Column (there should be 9 lines in this table
        id = Column(Integer, nullable=False, primary_key=True)
        verifications_id = Column(Integer, ForeignKey('VerificationSet.id'), nullable=False)
        name = Column(String(100))

        # Initialize the relationship
        verification_set = relationship('VerificationSet', backref=backref('Verification', lazy=True))

    class CompetitionSet(Base):
        __tablename__ = 'CompetitionSet'
        # Initialize the Column
        id = Column(Integer, nullable=False, primary_key=True)
        job_id = Column(Integer, ForeignKey('Job.id'), nullable=False)

        # Initialize the relationship
        job = relationship('Job', backref=backref('CompetitionSet', lazy=True))

    class Competition(Base):
        __tablename__ = 'Competition'
        # Initialize the Column (there should be 9 lines in this table
        id = Column(Integer, nullable=False, primary_key=True)
        verifications_id = Column(Integer, ForeignKey('CompetitionSet.id'), nullable=False)
        url = Column(String(1000))
        rating = Column(Integer)

        # Initialize the relationship
        competition_set = relationship('CompetitionSet', backref=backref('Competition', lazy=True))

    # create database
    Base.metadata.create_all(engine)

    # insert values from dict_merged
    for a_dict in dict_merged:
        # job
        job = Job(title=a_dict["titles"],
                  days_left_to_bid=a_dict["days left to bid"],
                  job_description=a_dict["description"],
                  url=a_dict["url"])
        # session.add(job)

        # budgets
        budget_set = BudgetSet(job=job)
        session.add(budget_set)

        # budget
        budget = BudgetInfo(budget_set=budget_set,
                            currency=a_dict["currency"],
                            per_hour=a_dict["per_hour"],
                            min=a_dict["min_value"],
                            max=a_dict["max_value"])
        # session.add(budget)

        # skills
        skill_set = SkillSet(job=job)
        session.add(skill_set)

        # add skill in catalogue
        for my_skill in [x.strip() for x in a_dict["skills"].split(',')]:
            skill = Skill(skillset=skill_set,
                          name=my_skill)
            # session.add(skill)

        # verifications
        verification_set = VerificationSet(job=job)
        session.add(verification_set)

        # add verification in catalogue
        for my_verif in a_dict["verified_traits_list"]:
            verification = Verification(verification_set=verification_set,
                                        name=my_verif)
            # session.add(verification)

        # verifications
        competition_set = CompetitionSet(job=job)
        session.add(competition_set)

        # add verification in catalogue
        for my_comp in a_dict["competition_list"]:
            competition = Competition(competition_set=competition_set, url=my_comp['url'],
                                      rating=my_comp['rating'])
            # session.add(competition)

    # Insert to the database
    session.commit()
    session.close()
